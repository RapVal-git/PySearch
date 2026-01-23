# Ghid de folosire: Web Search (HTML)

Acest ghid descrie pasii necesari pentru folosirea interfetei web (`web_cautare.html`)
cu autentificare si cautare securizata.

## 1. Pregatire (o singura data)
1) Instaleaza dependintele:
```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Importa utilizatorii din SAP (CSV):
```
python import_sap_users.py
```
Fisierul asteptat este `sap_export.csv` in acelasi folder.

3) Indexeaza documentele publice (doar incremental):
```
set INDEXING_FOLDER=\\192.168.27.44\ERP-implementare
python indexare_incrementala.py
```
Optional: indexeaza si folderul IT (acces doar grupului "it"), tot incremental:
```
set INDEXING_FOLDER=\\192.168.27.44\it\AI
python indexare_incrementala.py
```

## 2. Pornirea serverului (necesar la fiecare folosire)
```
python api_cautare_secured.py
```
Asteptat: serverul ruleaza pe `http://localhost:8000`.

## 3. Deschiderea interfetei web
Deschide fisierul `web_cautare.html` in browser (Chrome/Edge).

Daca API-ul ruleaza pe alt server, schimba linia:
```
const API_URL = 'http://localhost:8000';
```
cu IP-ul serverului.

## 4. Autentificare (first login)
1) Introdu email + parola.
2) Daca este prima logare, sistemul va cere setarea parolei.
3) Seteaza parola, apoi logheaza-te din nou.

## 5. Cautare documente
1) Scrie interogarea in tab-ul "Cautare Documente".
2) Apasa "Cauta".
3) Rezultatele apar daca userul are acces la folder.

## 6. Chat cu AI (optional)
Pentru chat local, porneste Ollama:
```
ollama run llama3
```
Apoi foloseste tab-ul "Chat cu AI".

## 7. Verificari rapide
- Daca nu esti logat, cautarea si chatul sunt blocate.
- Folderul `\\192.168.27.44\ERP-implementare` este public (toti userii).
- Folderul `\\192.168.27.44\it\AI` este accesibil doar grupului "it".

## 8. Troubleshooting
- "Sesiune invalida": logheaza-te din nou.
- Nu apar rezultate: verifica indexarea incrementala si calea folderului.
- Chat nu raspunde: asigura-te ca Ollama ruleaza.
