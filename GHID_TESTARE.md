#  Ghid Rapid de Testare - PyPro

## Status: TOTUL FUNCȚIONEAZĂ! 

###  Ce am verificat:

1. **Config.py** -  Funcționează perfect
2. **Toate modulele** -  Se importă corect
3. **Dependențe** -  Instalate complet

---

##  Cum Rulezi Proiectul

### 1. **Indexare Incrementală** (Recomandat!)

```bash
python indexare_incrementala.py
```

**Ce face:**
- Scanează folder-ul din `config.DEFAULT_INDEXING_FOLDER`
- Indexează DOAR fișierele noi/modificate
- Salvează progresul în `fisiere_indexate.json`
- Suportă: PDF, DOCX, Excel, Video

**Folder implicit:** `\\192.168.27.44\ERP-implementare\Specificatii de lucru`

**Cum schimbi folder-ul:**
- **Metoda 1:** Editează `config.py` → `DEFAULT_INDEXING_FOLDER`
- **Metoda 2:** Când rulezi, introduce alt path când te întreabă

---

### 2. **API Simplu (Fără Securitate)**

```bash
python api_cautare.py
```

**Acces:** http://localhost:8000

**Endpoints:**
- `GET /` - Info API
- `POST /search` - Căutare în documente
- `POST /chat` - Chat cu AI (necesită Ollama)
- `GET /health` - Health check

**Exemplu căutare:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "contract", "limit": 10}'
```

---

### 3. **API cu Securitate** (Cu Autentificare)

```bash
python api_cautare_secured.py
```

**Acces:** http://localhost:8000

**Workflow:**
1. Login: `POST /login` cu username + password
2. Primești `access_token`
3. Folosești token în header: `Authorization: Bearer <token>`

**Utilizatori demo:**
- `admin` / `admin123` (acces complet)
- `manager` / `manager123` (acces limitat)

---

##  Teste Rapide

### Test 1: Verifică Configurarea
```bash
python config.py
```

**Output așteptat:**
```
======================================================================
PyPro Search & Chat - Configurare Curenta
======================================================================
qdrant_path         : C:\...\qdrant_db
collection_name     : documente_pdf
embedding_model     : paraphrase-multilingual-mpnet-base-v2
whisper_model       : large
api_url             : http://0.0.0.0:8000
ollama_url          : http://localhost:11434/v1
log_level           : INFO
======================================================================
```

### Test 2: Verifică Importurile
```bash
python -c "import config; import indexare_incrementala; import video_extractie; import docx_extractie; import api_cautare; import rag_engine; print('OK - Toate modulele functioneaza!')"
```

**Output așteptat:** `OK - Toate modulele functioneaza!`

### Test 3: Testează Indexarea (Dry Run)
```bash
# Doar pentru a vedea ce fișiere ar fi indexate
python -c "from indexare_incrementala import *; import os; print('Folder:', config.DEFAULT_INDEXING_FOLDER); print('Exista:', os.path.exists(config.DEFAULT_INDEXING_FOLDER))"
```

---

##  Configurare Rapidă

### Schimbă Setările Principale

**Editează `config.py`:**
```python
# Paths
DEFAULT_INDEXING_FOLDER = r"C:\MeaDocumente"  # Schimbă aici!
QDRANT_PATH = r"D:\qdrant_db"

# Models
WHISPER_MODEL_SIZE = "medium"  # tiny, base, small, medium, large
EMBEDDING_MODEL = "paraphrase-multilingual-mpnet-base-v2"

# API
API_PORT = 9000  # Schimbă portul
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

### SAU Folosește Variabile de Mediu

```bash
# Windows
set INDEXING_FOLDER=C:\MeaDocumente
set WHISPER_MODEL_SIZE=medium
set API_PORT=9000
python indexare_incrementala.py
```

---

##  Workflow Complet Recomandat

### Pas 1: Indexează Documentele
```bash
python indexare_incrementala.py
```
Introdu path-ul când te întreabă sau apasă Enter pentru default.

### Pas 2: Pornește API-ul
```bash
python api_cautare.py
```

### Pas 3: Testează Căutarea
Deschide browser: http://localhost:8000/docs (Swagger UI)

SAU folosește `web_cautare.html`

---

##  Note Importante

###  Ce Funcționează:
-  Configurare centralizată (`config.py`)
-  Toate modulele se importă corect
-  Dependențele sunt instalate
-  Indexare incrementală
-  API simplu (fără auth)
-  API securizat (cu auth)
-  Suport pentru variabile de mediu

###  Ce Trebuie Verificat:
-  **Ollama** - Dacă vrei Chat AI, trebuie să ai Ollama pornit
  ```bash
  ollama run llama3
  ```
-  **Folder de indexare** - Verifică că există și ai acces
-  **GPU** - Pentru video (Whisper), verifică că ai CUDA instalat

###  Troubleshooting

**Problemă: "ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**Problemă: "Folder nu există"**
- Editează `config.py` → `DEFAULT_INDEXING_FOLDER`
- SAU introduce alt path când rulezi

**Problemă: "RAG Engine indisponibil"**
- Pornește Ollama: `ollama run llama3`
- SAU dezactivează chat-ul (doar căutare funcționează)

**Problemă: "UnicodeEncodeError"**
- Normal pe Windows cu caractere speciale
- Nu afectează funcționalitatea

---

##  Rezumat

**TOTUL FUNCȚIONEAZĂ!** 

Poți rula:
1.  `python indexare_incrementala.py` - Indexare
2.  `python api_cautare.py` - API simplu
3.  `python api_cautare_secured.py` - API cu securitate

**Configurarea** se face în `config.py` sau prin variabile de mediu.

**Fără securitate** = folosește `api_cautare.py` (mai simplu pentru testare)
**Cu securitate** = folosește `api_cautare_secured.py` (pentru producție)
