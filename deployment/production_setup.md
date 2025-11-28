# 🚀 Production Deployment Guide

## OPȚIUNEA 2: VPS/Cloud Server (Recomandat pentru Producție)

### Cerințe Server
- **CPU:** Minim 4 cores (8+ recomandat pentru 8TB)
- **RAM:** Minim 16GB (32GB+ recomandat)
- **Storage:** SSD cu spațiu suficient pentru Qdrant DB
- **GPU:** Opțional, pentru video transcription (Whisper)
- **OS:** Ubuntu 22.04 LTS (recomandat)

### Provideri Recomandați
1. **Hetzner** - Cel mai ieftin, performanță bună (€40-100/lună)
2. **DigitalOcean** - User-friendly, bun pentru început ($80-200/lună)
3. **AWS EC2** - Scalabil, dar mai scump
4. **Azure** - Bun dacă ai deja infrastructure Microsoft
5. **OVH** - Ieftin, datacenter în Europa

---

## 📋 Pas cu Pas: Deployment pe Ubuntu Server

### Pas 1: Pregătire Server

```bash
# Conectează-te la server via SSH
ssh root@your-server-ip

# Update sistem
sudo apt update && sudo apt upgrade -y

# Instalează dependențe
sudo apt install -y python3.10 python3-pip python3-venv git nginx certbot python3-certbot-nginx

# Instalează Docker (opțional, pentru Opțiunea 3)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install docker-compose -y
```

### Pas 2: Transferă Proiectul pe Server

**Opțiunea A: Git (Recomandat)**
```bash
cd /opt
sudo git clone https://github.com/your-username/pypro.git
cd pypro
```

**Opțiunea B: SCP (Transfer Direct)**
```powershell
# Din Windows (PowerShell)
scp -r C:\PyPro root@your-server-ip:/opt/pypro
```

**Opțiunea C: SFTP cu WinSCP**
- Descarcă WinSCP
- Conectează-te la server
- Copiază folderul C:\PyPro

### Pas 3: Setup Python Environment

```bash
cd /opt/pypro

# Creează virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalează dependențe
pip install --upgrade pip
pip install -r requirements.txt

# Instalează PyTorch cu CUDA (dacă ai GPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Pas 4: Configurare Qdrant

**Opțiunea A: Qdrant Local (Simplu)**
```bash
# Qdrant va folosi folderul local qdrant_db
# Nu necesită configurare suplimentară
```

**Opțiunea B: Qdrant Server (Recomandat pentru Producție)**
```bash
# Instalează Qdrant ca serviciu
docker run -d \
  --name qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant

# Modifică în cod: client = QdrantClient(url="http://localhost:6333")
```

### Pas 5: Configurare Systemd Service (Auto-start)

Creează fișier `/etc/systemd/system/pdf-search-api.service`:

```ini
[Unit]
Description=PDF Search API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pypro
Environment="PATH=/opt/pypro/venv/bin"
ExecStart=/opt/pypro/venv/bin/python api_cautare.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activează serviciul:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pdf-search-api
sudo systemctl start pdf-search-api
sudo systemctl status pdf-search-api
```

### Pas 6: Configurare Nginx (Reverse Proxy)

Creează fișier `/etc/nginx/sites-available/pdf-search`:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Sau IP-ul serverului

    # Mărește timeout pentru requests mari
    client_max_body_size 100M;
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    # API Endpoint
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Web Interface
    location / {
        root /opt/pypro;
        try_files $uri $uri/ /web_cautare.html;
        index web_cautare.html;
    }

    # Static files
    location /static/ {
        alias /opt/pypro/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Activează configurația:
```bash
sudo ln -s /etc/nginx/sites-available/pdf-search /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Pas 7: Configurare HTTPS (SSL Certificate)

```bash
# Obține certificat gratuit de la Let's Encrypt
sudo certbot --nginx -d your-domain.com

# Auto-renewal (se configurează automat)
sudo certbot renew --dry-run
```

### Pas 8: Configurare Firewall

```bash
# Permite doar porturile necesare
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### Pas 9: Serviciu de Indexare Automată

Creează `/etc/systemd/system/pdf-indexing.service`:

```ini
[Unit]
Description=PDF Indexing Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/pypro
Environment="PATH=/opt/pypro/venv/bin"
Environment="FOLDER_PDF=/mnt/documents"
ExecStart=/opt/pypro/venv/bin/python serviciu_indexare.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activează:
```bash
sudo systemctl enable pdf-indexing
sudo systemctl start pdf-indexing
```

### Pas 10: Monitoring și Logs

```bash
# Verifică logs API
sudo journalctl -u pdf-search-api -f

# Verifică logs indexare
sudo journalctl -u pdf-indexing -f

# Verifică logs Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🔒 Securitate

### 1. Autentificare API

Modifică `api_cautare.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

security = HTTPBearer()
API_KEYS = {
    "secret-key-1": "user1",
    "secret-key-2": "user2"
}

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return API_KEYS[token]

@app.post("/search")
async def search(request: SearchRequest, user: str = Depends(verify_token)):
    # Acum doar utilizatorii cu API key pot căuta
    ...
```

### 2. Rate Limiting

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/search")
@limiter.limit("10/minute")  # Max 10 requests per minute
async def search(request: Request, search_request: SearchRequest):
    ...
```

### 3. CORS Restricționat

În `api_cautare.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Nu "*"
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📊 Monitoring și Backup

### 1. Setup Monitoring cu Prometheus + Grafana

```bash
# Instalează prometheus-fastapi-instrumentator
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

### 2. Backup Automat

Creează script `/opt/pypro/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/backup/pypro"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Qdrant DB
tar -czf $BACKUP_DIR/qdrant_db_$DATE.tar.gz /opt/pypro/qdrant_db

# Backup fisiere indexate
cp /opt/pypro/fisiere_indexate.json $BACKUP_DIR/fisiere_indexate_$DATE.json

# Șterge backup-uri mai vechi de 7 zile
find $BACKUP_DIR -type f -mtime +7 -delete
```

Adaugă în crontab:
```bash
sudo crontab -e
# Adaugă:
0 2 * * * /opt/pypro/backup.sh
```

---

## 🎯 Testare Deployment

### 1. Test Local
```bash
curl http://localhost:8000/health
```

### 2. Test Extern
```bash
curl https://your-domain.com/api/health
```

### 3. Test Căutare
```bash
curl -X POST https://your-domain.com/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "contract", "limit": 5}'
```

---

## 📈 Scalare pentru Mulți Utilizatori

### 1. Horizontal Scaling (Multiple Workers)

În `api_cautare.py`:
```python
if __name__ == "__main__":
    import multiprocessing
    workers = multiprocessing.cpu_count() * 2 + 1
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=workers)
```

### 2. Load Balancing cu Nginx

```nginx
upstream pdf_search_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location /api/ {
        proxy_pass http://pdf_search_backend/;
    }
}
```

### 3. Caching cu Redis

```bash
pip install redis aioredis
```

```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/search")
async def search(request: SearchRequest):
    # Check cache
    cache_key = f"search:{request.query}:{request.limit}"
    cached = redis_client.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    # Perform search
    results = perform_search(request.query, request.limit)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(results))
    
    return results
```

---

## 💰 Estimare Costuri

### Server Hetzner (Recomandat)
- **CPX31** (4 vCPU, 8GB RAM, 160GB SSD): €13.90/lună
- **CPX41** (8 vCPU, 16GB RAM, 240GB SSD): €26.90/lună
- **CCX33** (8 vCPU, 32GB RAM, 240GB SSD): €52.90/lună

### Domeniu + SSL
- Domeniu: €10/an (Cloudflare, Namecheap)
- SSL: GRATUIT (Let's Encrypt)

### Total Estimat
- **Mic (10-50 utilizatori):** €15-30/lună
- **Mediu (50-200 utilizatori):** €50-80/lună
- **Mare (200+ utilizatori):** €100+/lună

---

## ✅ Checklist Final

- [ ] Server configurat și actualizat
- [ ] Python environment instalat
- [ ] Proiect transferat pe server
- [ ] Qdrant funcționează
- [ ] API pornește corect
- [ ] Nginx configurat
- [ ] SSL certificate instalat
- [ ] Firewall configurat
- [ ] Servicii auto-start activate
- [ ] Backup automat configurat
- [ ] Monitoring activ
- [ ] Teste de funcționare efectuate
- [ ] Documentație pentru utilizatori

---

## 🆘 Troubleshooting

### API nu pornește
```bash
sudo journalctl -u pdf-search-api -n 50
# Verifică erorile
```

### Nginx erori
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Qdrant nu se conectează
```bash
docker logs qdrant
# Sau verifică dacă folderul qdrant_db are permisiuni corecte
sudo chown -R www-data:www-data /opt/pypro/qdrant_db
```

### Out of Memory
```bash
# Adaugă swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```
