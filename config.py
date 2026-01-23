"""
Configurare centralizată pentru PyPro Search & Chat

Acest fișier conține toate setările proiectului.
Poți modifica valorile aici fără să atingi codul sursă.

Pentru a folosi variabile de mediu (recomandat pentru producție):
    set COLLECTION_NAME=documente_custom
    set QDRANT_PATH=D:\qdrant_data
"""

import os
from pathlib import Path


# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================

# Directorul de bază al proiectului
BASE_DIR = Path(__file__).parent.absolute()

# Calea către baza de date Qdrant (poate fi suprascrisă cu variabilă de mediu)
QDRANT_PATH = os.getenv("QDRANT_PATH", str(BASE_DIR / "qdrant_db"))

# Foldere implicite pentru indexare (lista)
INDEXING_FOLDERS = [
    r"\\192.168.27.44\ERP-implementare",
    r"\\192.168.27.44\it\AI",
]

# Override optional pentru un singur folder (gol implicit)
DEFAULT_INDEXING_FOLDER = os.getenv("INDEXING_FOLDER", "")

# Fișier pentru tracking documente indexate
INDEXED_FILES_JSON = str(BASE_DIR / "fisiere_indexate.json")


# ============================================================================
# QDRANT DATABASE
# ============================================================================

# Numele colecției în Qdrant
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "documente_pdf")

# Dimensiunea batch-ului pentru upload vectori
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))

# Dimensiunea vectorilor (depinde de modelul de embeddings)
VECTOR_SIZE = 768  # pentru paraphrase-multilingual-mpnet-base-v2

# Timeout pentru conexiunea Qdrant (secunde)
QDRANT_TIMEOUT = int(os.getenv("QDRANT_TIMEOUT", "10"))


# ============================================================================
# EMBEDDINGS MODEL
# ============================================================================

# Modelul pentru generare embeddings
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", 
    "paraphrase-multilingual-mpnet-base-v2"
)


# ============================================================================
# VIDEO PROCESSING (Whisper)
# ============================================================================

# Dimensiunea modelului Whisper
# Opțiuni: 'tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")

# Durata unui bloc de text din video (secunde)
# Chunk-urile mai mari = mai puțini vectori, dar context mai mare
VIDEO_BLOCK_DURATION = int(os.getenv("VIDEO_BLOCK_DURATION", "60"))

# Beam size pentru transcriere (mai mare = mai precis, dar mai lent)
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))


# ============================================================================
# DOCUMENT PROCESSING
# ============================================================================

# Număr de paragrafe per "pagină" pentru DOCX
DOCX_PARAGRAPHS_PER_PAGE = int(os.getenv("DOCX_PARAGRAPHS_PER_PAGE", "10"))

# Extensii de fișiere suportate
SUPPORTED_EXTENSIONS = {
    'pdf': ['.pdf'],
    'docx': ['.docx'],
    'excel': ['.xlsx', '.xls'],
    'video': ['.mp4', '.avi', '.mov', '.mkv'],
    'audio': ['.mp3', '.wav', '.m4a']
}

# Toate extensiile suportate (flatten)
ALL_SUPPORTED_EXTENSIONS = tuple(
    ext for exts in SUPPORTED_EXTENSIONS.values() for ext in exts
)


# ============================================================================
# API CONFIGURATION
# ============================================================================

# Host și port pentru API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# CORS - origini permise
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Număr maxim de rezultate pentru căutare
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "100"))

# Număr implicit de rezultate
DEFAULT_SEARCH_LIMIT = int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))


# ============================================================================
# RAG (Chat AI)
# ============================================================================

# URL pentru Ollama API
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

# Model Ollama implicit
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# Număr de documente de context pentru RAG
RAG_CONTEXT_LIMIT = int(os.getenv("RAG_CONTEXT_LIMIT", "5"))


# ============================================================================
# LOGGING
# ============================================================================

# Nivel de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Fișier pentru log-uri
LOG_FILE = str(BASE_DIR / "pypro.log")

# Format log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


# ============================================================================
# PERFORMANCE
# ============================================================================

# Număr de workers pentru procesare paralelă (None = auto-detect CPU cores)
NUM_WORKERS = int(os.getenv("NUM_WORKERS", "0")) or None

# Cache pentru model embeddings (economisește memorie)
CACHE_EMBEDDINGS_MODEL = os.getenv("CACHE_EMBEDDINGS_MODEL", "true").lower() == "true"


# ============================================================================
# SECURITY
# ============================================================================

# Secret key pentru JWT tokens (SCHIMBĂ ÎN PRODUCȚIE!)
SECRET_KEY = os.getenv("SECRET_KEY", "schimba-aceasta-cheie-in-productie-cu-ceva-foarte-secret")

# Algoritm pentru JWT
JWT_ALGORITHM = "HS256"

# Expirare token (ore)
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_config_summary():
    """Returnează un rezumat al configurației curente"""
    return {
        "qdrant_path": QDRANT_PATH,
        "collection_name": COLLECTION_NAME,
        "embedding_model": EMBEDDING_MODEL,
        "whisper_model": WHISPER_MODEL_SIZE,
        "api_url": f"http://{API_HOST}:{API_PORT}",
        "ollama_url": OLLAMA_BASE_URL,
        "log_level": LOG_LEVEL,
    }


def print_config():
    """Afișează configurația curentă (util pentru debugging)"""
    import sys
    # Fix pentru Windows console encoding
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    print("=" * 70)
    print("PyPro Search & Chat - Configurare Curenta")
    print("=" * 70)
    for key, value in get_config_summary().items():
        print(f"{key:20s}: {value}")
    print("=" * 70)


if __name__ == "__main__":
    # Testare configurare
    print_config()
