# Ghid rulare completa in Docker (Productie)

Acest ghid descrie pas cu pas cum pornesti toate componentele aplicatiei in Docker
folosind `docker-compose.production.yml` (Qdrant SERVER + Ollama + API + Nginx).

---

## 1) Cerinte
- Windows 10/11 cu WSL2 activat
- Docker Desktop instalat si pornit
- Spatiu liber pe disc (modelele Ollama pot fi mari)

---

## 2) Pregatire proiect
1. Verifica volumul cu documente in `docker-compose.production.yml`:
   - Exemplu: `//192.168.27.44/...:/app/pdf_source:ro`
   - Daca folosesti un share de retea, asigura-te ca Docker Desktop are acces.
2. (Optional) Copiaza `.env.example` in `.env` si seteaza valorile necesare.

---

## 3) Pornire stack (toate serviciile)
Ruleaza in folderul proiectului:
```bash
docker compose -f docker-compose.production.yml up -d --build
```
Verifica statusul:
```bash
docker compose -f docker-compose.production.yml ps
```

---

## 4) Pregatire Ollama (prima data)
Descarca modelul in containerul Ollama:
```bash
docker exec -it ollama ollama pull llama3
```
Testeaza ca Ollama raspunde:
```bash
curl http://localhost:11434/api/tags
```

---

## 5) Indexare documente
- Serviciul `indexare` ruleaza automat la pornire si apoi la fiecare 1 ora.
- Progresul se salveaza in `fisiere_indexate.json`, deci nu reproceseaza acelasi fisier.
- Daca vrei sa fortezi o runda imediata:
```bash
docker restart pdf-indexare
```

---

## 6) Acces aplicatie
- UI web (Nginx): `http://localhost`
- API (prin Nginx): `http://localhost`

Teste rapide:
```bash
curl http://localhost/health
```
```bash
curl -X POST http://localhost/search -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":3}"
```
```bash
curl -X POST http://localhost/chat -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":1}"
```

---

## 7) Loguri utile
```bash
docker compose -f docker-compose.production.yml logs -f api-1
```
```bash
docker compose -f docker-compose.production.yml logs -f indexare
```
```bash
docker compose -f docker-compose.production.yml logs -f qdrant
```
```bash
docker compose -f docker-compose.production.yml logs -f ollama
```

---

## 8) Oprire completa
```bash
docker compose -f docker-compose.production.yml down
```

---

## 9) Troubleshooting rapid
- Ollama nu raspunde: verifica `docker ps`, apoi `docker logs ollama`.
- Qdrant nu raspunde: `curl http://localhost:6333/health`.
- Folder de documente nu este accesibil: verifica permisiunile pentru Docker Desktop si calea montata.
