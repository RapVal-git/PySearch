#  Ghid Complet de Rulare: PyPro Search & Chat

Acest ghid îți explică pas cu pas cum să pornești întregul sistem, de la zero.

---

##  Productie (Docker, Qdrant SERVER)

Aceasta varianta ruleaza totul in containere si foloseste Qdrant SERVER.

###  Pasul 1: Cerinte
1. **Docker Desktop** instalat si pornit.

###  Pasul 2: Configurare
1. Copiaza `.env.example` in `.env` (optional) si seteaza valorile tale.
2. In `docker-compose.production.yml`, actualizeaza volumul cu documente:
   - `//192.168.27.44/...:/app/pdf_source:ro`
3. Pentru Chat, foloseste serviciul **ollama** din compose (recomandat).
   - Nu mai ai nevoie de `OLLAMA_BASE_URL` spre host, foloseste `http://ollama:11434/v1`

###  Pasul 3: Pornire productie
```bash
docker compose -f docker-compose.production.yml up -d --build
```

###  Pasul 4: Pregatire Ollama (prima data)
Trage modelul in container:
```bash
docker exec -it ollama ollama pull llama3
```
Test rapid:
```bash
curl http://localhost:11434/api/tags
```

###  Ce porneste
- **qdrant**: baza de date vectoriala (server) pe volum `./qdrant_storage`
- **ollama**: server LLM pe portul 11434 (modelul se salveaza in `./ollama`)
- **indexare**: ruleaza la pornire si apoi la fiecare 1 ora (serviciu de indexare)
- **api-1 / api-2**: API FastAPI
- **nginx**: proxy + UI web (serveste `web_cautare.html` pe portul 80)
- **redis / prometheus / grafana**: optionale (poti elimina daca nu le folosesti)

###  Acces
- UI web: `http://localhost`
- API (prin nginx): `http://localhost` (conform `nginx/nginx.conf`)

###  Testare rapida (API)
1. Verifica health:
```bash
curl http://localhost/health
```
2. Test chat (dupa ce ai indexat):
```bash
curl -X POST http://localhost/chat -H "Content-Type: application/json" -d "{\"query\":\"Test\",\"limit\":1}"
```

###  Reindexare
La trecerea pe Qdrant server trebuie sa refaci indexarea (datele nu mai sunt in `qdrant_db` local).

---

##  1. Cerințe Preliminare

Asigură-te că ai instalate:
1.  **Python 3.10+** ([Descarcă](https://www.python.org/downloads/))
2.  **Ollama** (pentru Chat AI) ([Descarcă](https://ollama.com/))
3.  **Dependențe Python:**
    Deschide un terminal în folderul proiectului și rulează:
    ```bash
    pip install -r requirements.txt
    pip install openai  # Necesar pentru Chat
    ```

---

##  2. Pasul 1: Indexarea Documentelor

Înainte să cauți, trebuie să "citești" documentele în baza de date.

1.  Pune fișierele tale (PDF, Excel, Word, Video) într-un folder (ex: `C:\Documente`).
2.  Rulează scriptul de indexare:
    ```bash
    python indexare_incrementala.py
    ```
3.  Când te întreabă, introdu calea folderului:
    ```text
    Introdu calea folderului: C:\Documente
    ```
4.  Așteaptă să termine. Vei vedea mesaje de genul `[NOU] Procesat: fisier.pdf`.

---

##  3. Pasul 2: Pornirea AI-ului (Ollama)

Pentru ca funcția de **Chat** să meargă, trebuie să ai Ollama pornit.

1.  Deschide un terminal nou.
2.  Rulează modelul (Llama 3 este recomandat):
    ```bash
    ollama run llama3
    ```
    *(Dacă nu îl ai, se va descărca automat - aprox 4GB).*
3.  Lasă terminalul deschis.

---

##  4. Pasul 3: Pornirea API-ului (Backend)

Acesta este "creierul" care face legătura între interfață și baza de date.

1.  Deschide un terminal nou în folderul proiectului.
2.  Rulează:
    ```bash
    python api_cautare.py
    ```
3.  Dacă vezi mesajul `Uvicorn running on http://0.0.0.0:8000`, ești gata!

---

##  5. Pasul 4: Folosirea Aplicației

Ai două opțiuni, alege-o pe cea care îți place:

### Opțiunea A: Aplicația Web (Browser)
*   **Cum:** Deschide fișierul `web_cautare.html` în Chrome/Edge.
*   **Ce oferă:** Căutare + Chat.
*   **Avantaj:** Nu trebuie instalat nimic pe alte calculatoare, doar deschizi fișierul.

### Opțiunea B: Aplicația Desktop (Windows)
*   **Cum:** Rulează în terminal:
    ```bash
    python gui_cautare.py
    ```
*   **Ce oferă:** Căutare + Chat într-o fereastră dedicată.
*   **Avantaj:** Se simte ca o aplicație nativă, rapidă.

---

##  Rezumat Comenzi (Cheatsheet)

| Acțiune | Comandă Terminal |
| :--- | :--- |
| **1. Indexare** | `python indexare_incrementala.py` |
| **2. Start AI** | `ollama run llama3` |
| **3. Start API** | `python api_cautare.py` |
| **4. Start App** | `python gui_cautare.py` (sau deschide HTML) |

---

##  Întrebări Frecvente

**Q: Trebuie să re-indexez mereu?**
A: Nu! Doar când adaugi fișiere noi. Rulezi `indexare_incrementala.py` și el va procesa **doar** ce e nou.

**Q: Chat-ul îmi dă eroare.**
A: Verifică dacă ai pornit Ollama (`ollama run llama3`) și dacă API-ul rulează (`python api_cautare.py`).

**Q: Pot accesa de pe alt calculator?**
A: Da! Dacă API-ul rulează pe server, modifică în `web_cautare.html` linia `const API_URL = 'http://localhost:8000';` cu IP-ul serverului (ex: `http://192.168.1.50:8000`).
