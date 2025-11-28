#  PyPro Search & Chat

Sistem avansat de căutare semantică (RAG) pentru documente interne, cu suport pentru PDF, Excel, Word și Video.

##  Cum să începi

Am pregătit un ghid detaliat pas cu pas pentru a rula proiectul:

 **[GHID_RULARE.md](GHID_RULARE.md)** 

##  Funcționalități Principale

*   **Căutare Semantică:** Găsește documente după înțeles, nu doar după cuvinte cheie.
*   **Chat cu AI (RAG):** Vorbește cu documentele tale și primește răspunsuri directe.
*   **Suport Multi-Format:** PDF, DOCX, XLSX (Excel), MP4 (Video cu transcriere).
*   **Interfețe Multiple:**
    *    **Desktop App:** Rapidă și nativă (`gui_cautare.py`).
    *    **Web App:** Accesibilă din browser (`web_cautare.html`).
    *    **API:** Pentru integrări (`api_cautare.py`).

##  Structură Proiect

*   `indexare_incrementala.py` - Scriptul care citește și indexează fișierele.
*   `api_cautare.py` - Serverul backend (Search + Chat).
*   `gui_cautare.py` - Aplicația Desktop.
*   `web_cautare.html` - Aplicația Web.
*   `rag_engine.py` - Modulul de inteligență artificială (Chat).
