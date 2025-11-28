# Deployment pe Rețea Locală

## Pas 1: Configurare API pentru Acces din Rețea

### 1.1 Modifică `api_cautare.py`

Schimbă linia finală din:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

În:
```python
uvicorn.run(app, host="0.0.0.0", port=8000, workers=4)
```

### 1.2 Verifică Firewall

**Windows:**
```powershell
# Permite trafic pe portul 8000
New-NetFirewallRule -DisplayName "PDF Search API" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

## Pas 2: Pornește Serverul

```bash
cd C:\PyPro
python api_cautare.py
```

## Pas 3: Testează Accesul

### Din rețeaua locală:
1. Găsește IP-ul serverului:
   ```powershell
   ipconfig
   # Caută "IPv4 Address" (ex: 192.168.1.100)
   ```

2. Accesează din browser pe alt PC:
   ```
   http://192.168.1.100:8000
   ```

3. Testează căutarea:
   ```
   http://192.168.1.100:8000/search?query=contract&limit=5
   ```

## Pas 4: Servește Web Interface

### Opțiunea A: Folosește Python HTTP Server
```bash
cd C:\PyPro
python -m http.server 8080
```

Acum accesează:
- API: `http://192.168.1.100:8000`
- Web UI: `http://192.168.1.100:8080/web_cautare.html`

### Opțiunea B: Integrează în FastAPI (Recomandat)

Modifică `api_cautare.py` să servească și HTML-ul.

## Limitări
- ❌ Funcționează doar în rețeaua locală
- ❌ Nu este securizat (fără HTTPS)
- ❌ Nu scalează pentru mulți utilizatori
- ❌ Se oprește când închizi terminalul

## Pentru Producție
Folosește **Opțiunea 2** sau **Opțiunea 3** de mai jos!
