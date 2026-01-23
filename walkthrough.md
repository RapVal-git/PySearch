# Walkthrough - RAG Pipeline cu Qdrant

Ghid complet pentru utilizarea sistemului de căutare în PDF-uri.

## Scripturi Disponibile

### 1. `indexare_incrementala.py` ? **RECOMANDAT**
**Cand sa-l folosesti:**
- Indexare initiala (prima rulare)
- Cand adaugi fisiere noi in folderele configurate
- Pentru update-uri regulate

**Cum functioneaza:**
- Calculeaza hash-ul fiecarui fisier
- Salveaza lista in `fisiere_indexate.json`
- Indexeaza doar fisiere noi sau modificate

**Rulare:**
```bash
python indexare_incrementala.py
```

---

### 2. `serviciu_indexare.py` - Indexare Automata
**Cand sa-l folosesti:**
- Pe server in productie
- Cand vrei indexare automata continua

**Cum functioneaza:**
- Ruleaza `indexare_incrementala.py` automat
- Verifica la fiecare **1 ora** (configurabil)

**Rulare:**
```bash
python serviciu_indexare.py
```

**Configurare interval:**
```python
# In serviciu_indexare.py, schimba:
schedule.every(1).hours.do(job)      # La fiecare ora
schedule.every(30).minutes.do(job)   # La fiecare 30 min
schedule.every().day.at("02:00").do(job)  # Zilnic la 2 AM
```

---

### 3. `api_cautare_secured.py` - REST API (Securizat)
**Cand sa-l folosesti:**
- In productie pe server
- Cand vrei sa integrezi cu alte aplicatii
- Pentru acces remote la cautare

**Rulare:**
```bash
python api_cautare_secured.py
```

**Acces:**
- API: `http://localhost:8000`
- Documentatie: `http://localhost:8000/docs`

**Exemplu request:**
```bash
curl -X POST http://localhost:8000/search   -H "Content-Type: application/json"   -d '{"query": "ion exchange", "limit": 5}'
```

---

### 4. Web Search (HTML)
**Cand sa-l folosesti:**
- Pentru interfata web cu login si cautare

**Rulare:**
- Deschide `web_cautare.html` in browser

---

## Workflow Recomandat

### Setup Inițial (Prima dată)
```bash
# 1. Instalează dependențe
pip install -r requirements.txt

# 2. Indexare completă (prima dată)
python indexare_incrementala.py
```

### Utilizare Zilnică (Local)
```bash
# Când adaugi PDF-uri noi
python indexare_incrementala.py

# Căutare
foloseste API-ul securizat sau web_cautare.html
```

### Deployment Server (Docker)
```bash
# Build și pornire
docker-compose up -d

# Serviciul va rula automat indexare_incrementala la fiecare oră
# API-ul va fi disponibil pe port 8000
```

---

## 🔧 Configurare

### Model AI
Folosește `paraphrase-multilingual-mpnet-base-v2`:
- Suportă română + engleză
- Căutare semantică (înțelege sensul, nu doar cuvinte)
- Vector size: 768

### Chunk Size
- **1024 caractere** (~200 cuvinte)
- Overlap: 100 caractere
- Configurabil în `procesare_text.py`

### Baza de Date
- **Qdrant** în Local Mode
- Salvată în `qdrant_db/`
- Backup: copiază folderul `qdrant_db/`

---

## 📊 Monitorizare

### Verifică progres indexare
```bash
# Vezi câte documente sunt indexate
# (în Python)
from qdrant_client import QdrantClient
client = QdrantClient(path="qdrant_db")
info = client.get_collection("documente_pdf")
print(f"Total vectori: {info.points_count}")
```

### Verifică fișiere indexate
```bash
# Vezi lista
cat fisiere_indexate.json
```

---

## 🐛 Troubleshooting

**Eroare: "No module named 'qdrant_client'"**
```bash
pip install -r requirements.txt
```

**Indexarea e prea lentă**
- Normal: ~5-10 chunks/secundă pe CPU
- Soluție: Folosește GPU sau reduce chunk size

**Rezultate căutare slabe**
- Verifică că ai folosit modelul `mpnet` (nu `MiniLM`)
- Crește chunk size la 1024+
- Indexează mai multe documente

**Vrei să ștergi tot și să re-indexezi**
```bash
# Șterge baza de date
rm -rf qdrant_db/
rm fisiere_indexate.json

# Re-indexează
python indexare_incrementala.py
```

---

## 📁 Fișiere Importante

- `qdrant_db/` - Baza de date vectorială
- `fisiere_indexate.json` - Tracking fișiere procesate
- `requirements.txt` - Dependențe Python
- `docker-compose.yml` - Configurare Docker
- `Dockerfile` - Container definition

---

## 🎯 Next Steps

1. **Testează local** cu `indexare_incrementala.py`
2. **Verifică căutarea** cu API securizat / web
3. **Deploy pe server** cu Docker
4. **Monitorizează** și ajustează intervalul de indexare

Pentru deployment Docker complet, vezi `deployment_guide.md`.
