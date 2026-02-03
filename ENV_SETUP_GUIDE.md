# Ghid complet rulare și testare PyPro Search & Chat (slim stack)

## 1. Curățarea mediului existent
- Oprește stack-ul vechi (dacă e încă activ):
  ```bash
  docker compose -f docker-compose.production.yml down
  ```
- Șterge imaginile mari dacă vrei să eliberezi spațiu:
  ```bash
  docker image rm pdf-api-1 pdf-api-2 pdf-api pysearch-indexare
  ```
- Opțional: curăță volumele/rețelele inactive:
  ```bash
  docker system prune --volumes
  ```

## 2. Pregătirea mediului slim
1. Asigură-te că ai fișierele adăugate (ex: `requirements_api.txt`, `Dockerfile.api`, `docker-compose.slim.yml`).
2. Rulează:
   ```bash
   docker compose -f docker-compose.slim.yml up -d --build
   ```
3. Verifică servicii healthy:
   ```bash
   docker compose -f docker-compose.slim.yml ps
   ```

## 3. Interfața web și testare HTML
- Deschide `http://localhost` în browserul tău; nginx servește `web_cautare.html`, cu tab-urile “Căutare Documente” și “Chat cu AI”.
- Dacă lucrezi de pe alt host sau vrei să deschizi fișierul manual, actualizează în `web_cautare.html` linia:
  ```js
  const API_URL = '/api';
  ```
  cu URL-ul corespunzător (ex: `http://192.168.1.50:8000`).
- Deschide fișierul `web_cautare.html` în editor ca să vezi exact structura pariurilor și a apelurilor Fetch.

## 4. Testare API (căutare + chat)
```bash
curl http://localhost/health
curl -X POST http://localhost/search -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":3}"
curl -X POST http://localhost/chat -H "Content-Type: application/json" -d "{\"query\":\"test\",\"limit\":1}"
```

## 5. Monitorizarea indexării și a folderelor
- Logurile indexării apar în `logs` (montate în `./logs`). Urmărește-le:
  ```bash
  docker compose -f docker-compose.slim.yml logs -f celery
  ```
- Fișierul `fisiere_indexate.json` ține evidența documentelor procesate, cu timestamp și cale. Poți vedea câte fișiere sunt indexate astfel:
  ```bash
  jq '. | length' fisiere_indexate.json
  ```
  sau, dacă nu ai `jq`, folosește Python:
  ```bash
  python - <<'PY'
  import json
  from pathlib import Path
  data = json.loads(Path('fisiere_indexate.json').read_text())
  print(f'{len(data)} fișiere indexate')
  PY
  ```
- Pentru detalii, citește conținutul `fisiere_indexate.json` și identifică ultimele căi procesate.

## 6. Oprirea și curățarea
```bash
docker compose -f docker-compose.slim.yml down
```

## 7. Sugestii utile
1. Dacă adaugi fișiere noi, repornește `celery`:
   ```bash
   docker compose -f docker-compose.slim.yml restart celery
   ```
2. Pentru debugging front-end, urmărește consola din browser și modifică `API_URL` dacă hostul se schimbă.
3. Compară dimensiunile imaginilor cu `docker images` pentru a confirma că API-ul e în continuare sub 2 GB.
