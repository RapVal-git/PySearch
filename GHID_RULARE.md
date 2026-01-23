#  Ghid Complet de Rulare: PyPro Search & Chat

Acest ghid îți explică pas cu pas cum să pornești întregul sistem, de la zero.

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

Inainte sa cauti, trebuie sa indexezi documentele folosind lista din `config.py`.

1. Configureaza folderele in `config.py`:
    ```bash
    INDEXING_FOLDERS = [
        r"\\192.168.27.44\ERP-implementare",
        r"\\192.168.27.44\it\AI",
    ]
    ```
2. Ruleaza indexarea incrementala:
    ```bash
    python indexare_incrementala.py
    ```
3. Asteapta sa termine. Vei vedea mesaje de genul `[NOU] Procesat: fisier.pdf`.

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
    python api_cautare_secured.py
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
| **3. Start API** | `python api_cautare_secured.py` |
| **4. Start App** | `python gui_cautare.py` (sau deschide HTML) |

---

##  Întrebări Frecvente

**Q: Trebuie să re-indexez mereu?**
A: Nu! Doar când adaugi fișiere noi. Rulezi `indexare_incrementala.py` și el va procesa **doar** ce e nou.

**Q: Chat-ul îmi dă eroare.**
A: Verifică dacă ai pornit Ollama (`ollama run llama3`) și dacă API-ul rulează (`python api_cautare_secured.py`).

**Q: Pot accesa de pe alt calculator?**
A: Da! Dacă API-ul rulează pe server, modifică în `web_cautare.html` linia `const API_URL = 'http://localhost:8000';` cu IP-ul serverului (ex: `http://192.168.1.50:8000`).
