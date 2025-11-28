#  Ghid de Testare - Indexare Incrementală

## Ce Testăm?

Sistemul de **indexare incrementală** verifică automat:
-  **Fișiere noi** → Se indexează
-  **Fișiere existente** → Se sar (nu se reindexează)
-  **Fișiere modificate** → Se reindexează automat

##  Metode de Testare

### Metoda 1: Test Automat Complet (Recomandat)

Rulează suite-ul complet de teste:

```bash
python test_indexare_incrementala.py
```

**Ce face:**
- Creează un folder de test cu fișiere PDF dummy
- Testează indexarea inițială
- Testează detectarea fișierelor existente
- Testează detectarea modificărilor
- Testează adăugarea de fișiere noi
- Verifică structura `fisiere_indexate.json`
- Curăță automat după teste

**Output așteptat:**
```

     TEST SUITE: INDEXARE INCREMENTALĂ                     


============================================================
SETUP: Pregătire Mediu de Test
============================================================

 Creat folder de test: test_indexare
 Backup creat: fisiere_indexate.json.backup

============================================================
TEST 1: Indexare Fișiere Noi
============================================================

...

 TOATE TESTELE AU TRECUT: 5/5
```

---

### Metoda 2: Test Manual Interactiv

Pentru explorare pas cu pas:

```bash
python test_manual_indexare.py
```

**Meniu interactiv:**
```
 TEST MANUAL - INDEXARE INCREMENTALĂ

Opțiuni:
  1. Afișează status tracking curent
  2. Verifică un fișier specific
  3. Compară două fișiere
  4. Simulează modificare fișier
  5. Afișează conținut fisiere_indexate.json (raw)
  0. Ieșire
```

**Exemple de utilizare:**

**Opțiunea 1** - Vezi ce fișiere sunt tracked:
```
 STATUS TRACKING CURENT
 Total fișiere tracked: 15

Lista fișiere indexate:
 1. contract_2024.pdf                          
    Cale: C:\Documents\contract_2024.pdf
    Hash: 5d41402abc4b2a76b9719d911017c592
```

**Opțiunea 2** - Verifică un fișier:
```
 VERIFICARE FIȘIER: document.pdf
Hash curent: 5d41402abc4b2a76b9719d911017c592

 Fișierul ESTE în tracking
   Hash tracked: 5d41402abc4b2a76b9719d911017c592

 Hash-urile COINCID
   → Fișierul va fi SĂRIT (deja indexat)
```

---

### Metoda 3: Test Manual Rapid

**Pas 1: Indexare Inițială**

```bash
python indexare_incrementala.py
```

Introdu calea către un folder cu PDF-uri când ești întrebat.

**Output așteptat:**
```
Scanare folder: C:\Documents...
  [NOU/MODIFICAT] document1.pdf
  [NOU/MODIFICAT] document2.pdf
  [NOU/MODIFICAT] document3.pdf

Gasite 3 fisiere noi/modificate din 3 total.
```

**Pas 2: Verifică Tracking**

Deschide `fisiere_indexate.json`:

```json
{
  "C:\\Documents\\document1.pdf": "5d41402abc4b2a76b9719d911017c592",
  "C:\\Documents\\document2.pdf": "7d793037a0760186574b0282f2f435e7",
  "C:\\Documents\\document3.pdf": "6df23dc03f9b54cc38a0fc1483df6e21"
}
```

**Pas 3: Rulează Din Nou (Fără Modificări)**

```bash
python indexare_incrementala.py
```

**Output așteptat:**
```
Scanare folder: C:\Documents...
  [DEJA INDEXAT] document1.pdf
  [DEJA INDEXAT] document2.pdf
  [DEJA INDEXAT] document3.pdf

Nu sunt fisiere noi de indexat!
```

 **TEST PASSED** - Fișierele existente sunt detectate corect!

**Pas 4: Modifică un Fișier**

Deschide `document1.pdf` și adaugă ceva text, apoi salvează.

```bash
python indexare_incrementala.py
```

**Output așteptat:**
```
Scanare folder: C:\Documents...
  [NOU/MODIFICAT] document1.pdf    ← Detectat ca modificat!
  [DEJA INDEXAT] document2.pdf
  [DEJA INDEXAT] document3.pdf

Gasite 1 fisiere noi/modificate din 3 total.
```

 **TEST PASSED** - Modificările sunt detectate!

**Pas 5: Adaugă Fișier Nou**

Copiază un PDF nou în folder.

```bash
python indexare_incrementala.py
```

**Output așteptat:**
```
Scanare folder: C:\Documents...
  [DEJA INDEXAT] document1.pdf
  [DEJA INDEXAT] document2.pdf
  [DEJA INDEXAT] document3.pdf
  [NOU/MODIFICAT] document4_nou.pdf    ← Fișier nou detectat!

Gasite 1 fisiere noi/modificate din 4 total.
```

 **TEST PASSED** - Fișierele noi sunt detectate!

---

##  Verificare Manuală a Hash-urilor

Dacă vrei să verifici manual hash-urile:

```python
from indexare_incrementala import calculeaza_hash_fisier

# Calculează hash pentru un fișier
hash1 = calculeaza_hash_fisier("document.pdf")
print(f"Hash: {hash1}")

# Modifică fișierul, apoi recalculează
hash2 = calculeaza_hash_fisier("document.pdf")
print(f"Hash nou: {hash2}")

# Compară
if hash1 != hash2:
    print("Fișierul a fost modificat!")
```

---

##  Scenarii de Test

### Scenariu 1: Indexare Inițială
- **Input:** Folder cu 10 PDF-uri noi
- **Așteptat:** Toate 10 fișiere marcate ca `[NOU/MODIFICAT]`
- **Verificare:** `fisiere_indexate.json` conține 10 intrări

### Scenariu 2: Reindexare Fără Modificări
- **Input:** Același folder, fără modificări
- **Așteptat:** Toate 10 fișiere marcate ca `[DEJA INDEXAT]`
- **Verificare:** Mesaj "Nu sunt fisiere noi de indexat!"

### Scenariu 3: Modificare Fișier
- **Input:** Modifică 1 fișier din 10
- **Așteptat:** 1 fișier `[NOU/MODIFICAT]`, 9 `[DEJA INDEXAT]`
- **Verificare:** Hash-ul fișierului modificat s-a schimbat în JSON

### Scenariu 4: Adăugare Fișiere Noi
- **Input:** Adaugă 5 PDF-uri noi în folder
- **Așteptat:** 5 fișiere `[NOU/MODIFICAT]`, 10 `[DEJA INDEXAT]`
- **Verificare:** `fisiere_indexate.json` conține 15 intrări

### Scenariu 5: Ștergere Fișier
- **Input:** Șterge 1 fișier din folder
- **Așteptat:** 9 fișiere `[DEJA INDEXAT]`
- **Verificare:** Fișierul șters rămâne în JSON (nu afectează funcționalitatea)

---

##  Troubleshooting

### Problema: Toate fișierele sunt marcate ca NOI de fiecare dată

**Cauză:** `fisiere_indexate.json` nu se salvează sau se șterge

**Soluție:**
1. Verifică dacă fișierul există: `dir fisiere_indexate.json`
2. Verifică permisiunile de scriere în folder
3. Verifică logs pentru erori de salvare

### Problema: Fișierele modificate nu sunt detectate

**Cauză:** Hash-ul nu se schimbă (fișierul nu s-a modificat efectiv)

**Soluție:**
1. Verifică că ai salvat modificările
2. Compară hash-urile manual:
   ```python
   from indexare_incrementala import calculeaza_hash_fisier
   print(calculeaza_hash_fisier("fisier.pdf"))
   ```

### Problema: `fisiere_indexate.json` este gol

**Cauză:** Indexarea nu s-a finalizat cu succes

**Soluție:**
1. Verifică logs pentru erori
2. Rulează cu un folder mic pentru test
3. Verifică că Qdrant funcționează

---

##  Checklist de Testare

Înainte de deployment pe server, verifică:

- [ ] Test automat complet rulează fără erori
- [ ] Fișierele noi sunt detectate corect
- [ ] Fișierele existente sunt sărite
- [ ] Modificările sunt detectate
- [ ] `fisiere_indexate.json` se creează și se actualizează
- [ ] Hash-urile sunt MD5 valide (32 caractere hex)
- [ ] Căile în JSON sunt absolute
- [ ] Sistemul funcționează cu foldere mari (100+ fișiere)
- [ ] Sistemul funcționează cu subfoldere
- [ ] Sistemul funcționează cu PDF, DOCX și VIDEO

---

##  Performance Testing

Pentru a testa cu volume mari:

```bash
# Creează 1000 de fișiere dummy pentru test
python -c "
import os
for i in range(1000):
    with open(f'test_folder/dummy_{i:04d}.pdf', 'w') as f:
        f.write(f'%PDF-1.4\nTest {i}\n%%EOF')
"

# Rulează indexarea și măsoară timpul
import time
start = time.time()
indexare_incrementala('test_folder')
print(f'Timp: {time.time() - start:.2f}s')
```

**Benchmark așteptat:**
- 100 fișiere: ~30-60 secunde
- 1000 fișiere: ~5-10 minute
- 10000 fișiere: ~1-2 ore

---

##  Concluzie

Sistemul de indexare incrementală este **production-ready** și funcționează corect dacă:
1.  Toate testele automate trec
2.  Fișierele existente sunt sărite (nu se reindexează)
3.  Modificările sunt detectate automat
4.  `fisiere_indexate.json` se actualizează corect

**Gata pentru deployment pe server!** 
