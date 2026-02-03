# Ghid complet rulare și testare PyPro Search & Chat în Docker

## 1. Cerințe inițiale
- Windows 10/11 cu WSL2 activat.
- Docker Desktop instalat și pornit.
- Copiază `.env.example` în `.env` (opțional) și ajustează valorile locale.
- Verifică că volumul documentelor din `docker-compose.production.yml` este corect montat (ex: `//192.168.27.44/...:/app/pdf_source:ro`).

## 2. Pornirea stack-ului complet
1. Din directorul rădăcină al proiectului rulează:
   ```bash
   docker compose -f docker-compose.production.yml up -d --build
   ```
2. Confirmă starea serviciilor:
   ```bash
   docker compose -f docker-compose.production.yml ps
   ```

## 3. Pregătirea modelului Ollama
1. Descarcă modelul în container:
   ```bash
   docker exec -it ollama ollama pull llama3
   ```
2. Verifică că Ollama răspunde:
   ```bash
   curl http://localhost:11434/api/tags
   ```

## 4. Indexarea documentelor
- Serviciul `indexare` rulează automat la pornire și din oră în oră.
- Dacă vrei o rundă imediată:
  ```bash
  docker restart pdf-indexare
  ```

## 5. Testarea API-ului prin nginx
1. Health check:
   ```bash
   curl http://localhost/health
   ```
2. Test căutare:
   ```bash
   curl -X POST http://localhost/search -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":3}"
   ```
3. Test chat:
   ```bash
   curl -X POST http://localhost/chat -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":1}"
   ```

## 6. Monitorizare loguri
- API: `docker compose -f docker-compose.production.yml logs -f api-1`
- Indexare: `docker compose -f docker-compose.production.yml logs -f indexare`
- Qdrant: `docker compose -f docker-compose.production.yml logs -f qdrant`
- Ollama: `docker compose -f docker-compose.production.yml logs -f ollama`

## 7. Accesul la interfața web
- Deschide `http://localhost` în browser; nginx servește `web_cautare.html`.
- Dacă folosești pagina direct (fără nginx) sau un alt host, ajustează în `web_cautare.html` linia:
  ```js
  const API_URL = '/api';
  ```
  cu adresa API-ului (ex: `http://192.168.1.50:8000`).

## 8. Oprirea stack-ului
```bash
docker compose -f docker-compose.production.yml down
```
