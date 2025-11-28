from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import uvicorn
from typing import List, Optional
import config

# Import RAG Engine (pentru Chat)
try:
    from rag_engine import RAGEngine
except ImportError:
    RAGEngine = None

app = FastAPI(title="PyPro Search API (Open Access)", version="2.0.0")

# Configurare CORS (din config.py)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurare Globală (din config.py)
collection_name = config.COLLECTION_NAME
qdrant_path = config.QDRANT_PATH
model = None
client = None
rag_engine = None

# ============================================================================
# MODELE DE DATE (Request/Response)
# ============================================================================

class SearchRequest(BaseModel):
    query: str
    limit: int = config.DEFAULT_SEARCH_LIMIT

class SearchResult(BaseModel):
    text: str
    score: float
    source: str
    page: int
    document_type: str = "DOC"

class ChatRequest(BaseModel):
    query: str
    limit: int = config.RAG_CONTEXT_LIMIT

class ChatResponse(BaseModel):
    answer: str
    context_used: List[SearchResult]

# ============================================================================
# INITIALIZARE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    global model, client, rag_engine
    
    print(" Pornire API...")
    
    print("1. Încărcare model embedding...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)
    
    print("2. Conectare la Qdrant...")
    client = QdrantClient(path=qdrant_path)
    
    print("3. Inițializare RAG Engine (Local)...")
    try:
        rag_engine = RAGEngine(provider="local", model_name=config.OLLAMA_MODEL)
        print(" RAG Engine activat!")
    except Exception as e:
        print(f" RAG Engine indisponibil: {e}")
        print("   (Chat-ul nu va funcționa, dar Căutarea da)")

    print(" API Gata de utilizare!")

# ============================================================================
# ENDPOINTS (Fără Securitate)
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "PyPro Search API", 
        "mode": "Open Access (No Auth)",
        "status": "online"
    }

@app.post("/search", response_model=List[SearchResult])
async def search(request: SearchRequest):
    """
    Căutare simplă în documente.
    Nu necesită autentificare.
    """
    try:
        # 1. Vectorizare query
        query_vector = model.encode(request.query).tolist()
        
        # 2. Căutare în Qdrant
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=request.limit
        ).points
        
        # 3. Formatare rezultate
        search_results = []
        for hit in results:
            search_results.append(SearchResult(
                text=hit.payload.get('text_chunk', ''),
                score=hit.score,
                source=hit.payload.get('sursa_fisier', 'Unknown'),
                page=hit.payload.get('pagina', 0),
                document_type=hit.payload.get('tip_document', 'DOC')
            ))
        
        return search_results
        
    except Exception as e:
        print(f"Eroare search: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat cu AI-ul despre documente.
    Nu necesită autentificare.
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG Engine nu este activat.")

    try:
        # 1. Căutare context (Retrieval)
        query_vector = model.encode(request.query).tolist()
        
        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=request.limit
        ).points
        
        if not results:
            return ChatResponse(
                answer="Nu am găsit informații relevante în documente.",
                context_used=[]
            )

        # 2. Pregătire context
        context_chunks = [r.payload for r in results]
        
        # 3. Generare răspuns (Generation)
        answer = rag_engine.genereaza_raspuns(request.query, context_chunks)
        
        # 4. Formatare surse
        sources = []
        for hit in results:
            sources.append(SearchResult(
                text=hit.payload.get('text_chunk', ''),
                score=hit.score,
                source=hit.payload.get('sursa_fisier', 'Unknown'),
                page=hit.payload.get('pagina', 0),
                document_type=hit.payload.get('tip_document', 'DOC')
            ))
            
        return ChatResponse(
            answer=answer,
            context_used=sources
        )

    except Exception as e:
        print(f"Eroare chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
