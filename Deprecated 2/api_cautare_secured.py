from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import uvicorn
from typing import Optional
import secrets
import config

# Import configurare autentificare
from auth_config import (
    verify_password, 
    get_user_role, 
    filter_results_by_user,
    get_allowed_folders,
    get_allowed_folders,
    USERS
)

# Import RAG Engine
from rag_engine import RAGEngine

app = FastAPI(title="PDF Search API (Secured)", version="2.0.0")

# Security schemes
security_basic = HTTPBasic()
security_bearer = HTTPBearer()

# Configurare CORS (din config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurare (din config.py)
collection_name = config.COLLECTION_NAME
qdrant_path = config.QDRANT_PATH
model = None
client = None
rag_engine = None  # Motorul RAG

# API Keys storage (Ã®n producÈ›ie, foloseÈ™te bazÄƒ de date)
API_KEYS = {}


class SearchRequest(BaseModel):
    query: str
    limit: int = config.DEFAULT_SEARCH_LIMIT


class SearchResult(BaseModel):
    text: str
    score: float
    source: str
    page: int
    document_type: str = "PDF"


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class ChatRequest(BaseModel):
    query: str
    limit: int = config.RAG_CONTEXT_LIMIT  # CÃ¢te chunk-uri folosim pentru context
    provider: str = "local"  # "local" sau "openai"


class ChatResponse(BaseModel):
    answer: str
    context_used: list[SearchResult]


# ============================================================================
# AUTENTIFICARE
# ============================================================================

def verify_basic_auth(credentials: HTTPBasicCredentials = Depends(security_basic)) -> str:
    """VerificÄƒ autentificare Basic (username + password)"""
    username = credentials.username
    password = credentials.password
    
    if not verify_password(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username sau parolÄƒ incorectÄƒ",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return username


def verify_bearer_token(credentials: HTTPAuthorizationCredentials = Depends(security_bearer)) -> str:
    """VerificÄƒ token Bearer (API key)"""
    token = credentials.credentials
    
    if token not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid sau expirat",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return API_KEYS[token]


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    global model, client, rag_engine
    print("Incarcare model...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)
    print("Conectare la Qdrant...")
    client = QdrantClient(path=qdrant_path)
    
    print("IniÈ›ializare RAG Engine (Local)...")
    try:
        # PoÈ›i schimba provider="openai" È™i api_key="sk-..." dacÄƒ vrei Cloud
        global rag_engine
        rag_engine = RAGEngine(provider="local", model_name=config.OLLAMA_MODEL)
        print("RAG Engine gata!")
    except Exception as e:
        print(f"âš ï¸ Avertisment: RAG Engine nu a putut fi iniÈ›ializat: {e}")

    print("API gata!")


@app.get("/")
async def root():
    return {
        "message": "PDF Search API (Secured)", 
        "status": "running",
        "version": "2.0.0",
        "authentication": "required"
    }


@app.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login endpoint - returneazÄƒ API token
    
    Exemplu:
    POST /login
    {
        "username": "admin",
        "password": "admin123"
    }
    """
    if not verify_password(request.username, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username sau parolÄƒ incorectÄƒ"
        )
    
    # GenereazÄƒ API key
    api_key = secrets.token_urlsafe(32)
    API_KEYS[api_key] = request.username
    
    role = get_user_role(request.username)
    
    return LoginResponse(
        access_token=api_key,
        token_type="bearer",
        username=request.username,
        role=role
    )


@app.get("/me")
async def get_current_user(username: str = Depends(verify_bearer_token)):
    """ReturneazÄƒ informaÈ›ii despre utilizatorul curent"""
    role = get_user_role(username)
    allowed_folders = get_allowed_folders(username)
    
    return {
        "username": username,
        "role": role,
        "name": USERS[username]["name"],
        "allowed_folders": allowed_folders
    }


@app.post("/search", response_model=list[SearchResult])
async def search(
    request: SearchRequest, 
    username: str = Depends(verify_bearer_token)
):
    """
    CautÄƒ Ã®n documentele indexate (cu control acces)
    
    NecesitÄƒ autentificare Bearer token.
    Rezultatele sunt filtrate bazat pe permisiunile utilizatorului.
    
    Exemplu:
    POST /search
    Headers: Authorization: Bearer <token>
    {
        "query": "contract",
        "limit": 10
    }
    """
    try:
        # GenereazÄƒ embedding pentru query
        query_vector = model.encode(request.query).tolist()
        
        # CautÄƒ Ã®n Qdrant (ia mai multe rezultate pentru filtrare)
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=request.limit * 3  # Ia mai multe pentru filtrare
        ).points
        
        # FiltreazÄƒ rezultatele bazat pe permisiuni
        filtered_results = filter_results_by_user(
            [{"payload": r.payload, "score": r.score} for r in results],
            username
        )
        
        # LimiteazÄƒ la numÄƒrul cerut
        filtered_results = filtered_results[:request.limit]
        
        # FormateazÄƒ rezultatele
        search_results = []
        for hit in filtered_results:
            search_results.append(SearchResult(
                text=hit["payload"].get('text_chunk', ''),
                score=hit["score"],
                source=hit["payload"].get('sursa_fisier', 'Unknown'),
                page=hit["payload"].get('pagina', 0),
                document_type=hit["payload"].get('tip_document', 'PDF')
            ))
        
        # Log cÄƒutare (opÈ›ional)
        print(f"[SEARCH] User: {username}, Query: '{request.query}', Results: {len(search_results)}")
        
        return search_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    username: str = Depends(verify_bearer_token)
):
    """
    RAG Chat Endpoint - RÄƒspunde la Ã®ntrebÄƒri folosind documentele
    
    Exemplu:
    POST /chat
    {
        "query": "Cum Ã®mi iau concediu?",
        "limit": 5
    }
    """
    try:
        # 1. CautÄƒ documente relevante (Retrieval)
        query_vector = model.encode(request.query).tolist()
        
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=request.limit * 3 # Mai multe pentru filtrare
        ).points
        
        # 2. FiltreazÄƒ rezultatele (Security)
        filtered_results = filter_results_by_user(
            [{"payload": r.payload, "score": r.score} for r in results],
            username
        )
        filtered_results = filtered_results[:request.limit]
        
        if not filtered_results:
            return ChatResponse(
                answer="Nu am gÄƒsit documente relevante la care sÄƒ ai acces pentru a rÄƒspunde la aceastÄƒ Ã®ntrebare.",
                context_used=[]
            )

        # 3. PregÄƒteÈ™te contextul pentru LLM
        context_chunks = [r["payload"] for r in filtered_results]
        
        # 4. GenereazÄƒ rÄƒspuns (Generation)
        if not rag_engine:
            raise HTTPException(status_code=503, detail="RAG Engine nu este disponibil.")
            
        answer = rag_engine.genereaza_raspuns(request.query, context_chunks)
        
        # 5. FormateazÄƒ sursele folosite
        sources = []
        for hit in filtered_results:
            sources.append(SearchResult(
                text=hit["payload"].get('text_chunk', ''),
                score=hit["score"],
                source=hit["payload"].get('sursa_fisier', 'Unknown'),
                page=hit["payload"].get('pagina', 0),
                document_type=hit["payload"].get('tip_document', 'PDF')
            ))
            
        return ChatResponse(
            answer=answer,
            context_used=sources
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """Health check endpoint (fÄƒrÄƒ autentificare)"""
    return {"status": "healthy"}


@app.get("/stats")
async def stats(username: str = Depends(verify_bearer_token)):
    """
    Statistici despre baza de date
    Doar pentru admin
    """
    role = get_user_role(username)
    
    if role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces interzis. Doar administratorii pot vedea statistici."
        )
    
    try:
        collection_info = client.get_collection(collection_name)
        
        return {
            "total_documents": collection_info.points_count,
            "vector_size": 768,
            "collection_name": collection_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
