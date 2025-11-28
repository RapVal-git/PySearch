# Walkthrough - RAG Pipeline cu Qdrant

Ghid complet pentru utilizarea sistemului de căutare în PDF-uri.

## 📚 Scripturi Disponibile

### 1. `indexare_folder_qdrant.py` - Indexare Completă
**Când să-l folosești:**
- Prima indexare a unui folder
- După ce ștergi baza de date (`qdrant_db/`)
- Când vrei să re-indexezi totul de la zero

**Cum funcționează:**
- Scanează tot folderul recursiv
- Indexează TOATE PDF-urile găsite
- Nu verifică dacă sunt deja indexate

**Rulare:**
```bash
python indexare_folder_qdrant.py
```

---

### 2. `indexare_incrementala.py` ⭐ **RECOMANDAT**
**Când să-l folosești:**
- După prima indexare
- Când adaugi PDF-uri noi în folder
- Când modifici PDF-uri existente
- Pentru update-uri regulate

**Cum funcționează:**
- Calculează hash-ul fiecărui PDF
- Salvează lista în `fisiere_indexate.json`
- Indexează doar fișiere noi sau modificate
- **Mult mai rapid** decât indexarea completă

**Rulare:**
```bash
python indexare_incrementala.py
```

**Avantaje:**
- ✅ Detectează automat fișiere noi
- ✅ Detectează fișiere modificate
- ✅ Salvează progresul după fiecare fișier
- ✅ Nu re-procesează ce e deja indexat

---

### 3. `serviciu_indexare.py` - Indexare Automată
**Când să-l folosești:**
- Pe server în producție
- Când vrei indexare automată continuă
- În Docker deployment

**Cum funcționează:**
- Rulează `indexare_incrementala.py` automat
- Verifică la fiecare **1 oră** (configurabil)
- Rulează continuu în background

**Rulare:**
```bash
python serviciu_indexare.py
```

**Configurare interval:**
```python
# În serviciu_indexare.py, schimbă:
schedule.every(1).hours.do(job)      # La fiecare oră
schedule.every(30).minutes.do(job)   # La fiecare 30 min
schedule.every().day.at("02:00").do(job)  # Zilnic la 2 AM
```

---

### 4. `cautare_qdrant.py` - Căutare Interactivă
**Când să-l folosești:**
- Pentru căutări manuale în terminal
- Testing și debugging

**Rulare:**
```bash
python cautare_qdrant.py
```

**Configurare număr rezultate:**
```python
# În cautare_qdrant.py, linia 46:
limit=10  # Schimbă cu câte rezultate vrei
```

---

### 5. `api_cautare.py` - REST API
**Când să-l folosești:**
- În producție pe server
- Când vrei să integrezi cu alte aplicații
- Pentru acces remote la căutare

**Rulare:**
```bash
python api_cautare.py
```

**Acces:**
- API: `http://localhost:8000`
- Documentație: `http://localhost:8000/docs`

**Exemplu request:**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ion exchange", "limit": 5}'
```

---

## 🚀 Workflow Recomandat

### Setup Inițial (Prima dată)
```bash
# 1. Instalează dependențe
pip install -r requirements.txt

# 2. Indexare completă (prima dată)
python indexare_folder_qdrant.py
```

### Utilizare Zilnică (Local)
```bash
# Când adaugi PDF-uri noi
python indexare_incrementala.py

# Căutare
python cautare_qdrant.py
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
python indexare_folder_qdrant.py
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
2. **Verifică căutarea** cu `cautare_qdrant.py`
3. **Deploy pe server** cu Docker
4. **Monitorizează** și ajustează intervalul de indexare

Pentru deployment Docker complet, vezi `deployment_guide.md`.
