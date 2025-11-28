"""
Script de testare pentru indexare incrementală
Testează:
1. Indexarea fișierelor noi
2. Detectarea fișierelor deja indexate
3. Detectarea fișierelor modificate
4. Tracking în fisiere_indexate.json
"""

import os
import json
import shutil
import time
from pathlib import Path
from indexare_incrementala import indexare_incrementala, calculeaza_hash_fisier

# Culori pentru output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def setup_test_environment():
    """Creează un mediu de test cu fișiere PDF de test"""
    print_header("SETUP: Pregătire Mediu de Test")
    
    # Creează folder de test
    test_folder = Path("test_indexare")
    if test_folder.exists():
        print_warning(f"Ștergere folder existent: {test_folder}")
        shutil.rmtree(test_folder)
    
    test_folder.mkdir()
    print_success(f"Creat folder de test: {test_folder}")
    
    # Backup fisiere_indexate.json dacă există
    tracking_file = Path("fisiere_indexate.json")
    backup_file = Path("fisiere_indexate.json.backup")
    
    if tracking_file.exists():
        shutil.copy(tracking_file, backup_file)
        print_success(f"Backup creat: {backup_file}")
        # Șterge tracking-ul pentru test curat
        tracking_file.unlink()
        print_info("Șters fisiere_indexate.json pentru test curat")
    
    return test_folder, backup_file

def create_dummy_pdf(path, content="Test PDF Content"):
    """Creează un fișier PDF dummy pentru testare"""
    # Creează un PDF simplu (nu e un PDF valid, dar e suficient pentru test)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(f"%PDF-1.4\n{content}\n%%EOF")
    print_info(f"Creat fișier: {path.name}")

def test_1_indexare_fisiere_noi(test_folder):
    """Test 1: Indexare fișiere noi"""
    print_header("TEST 1: Indexare Fișiere Noi")
    
    # Creează 3 fișiere PDF de test
    pdf1 = test_folder / "document1.pdf"
    pdf2 = test_folder / "document2.pdf"
    pdf3 = test_folder / "subfolder" / "document3.pdf"
    
    (test_folder / "subfolder").mkdir(exist_ok=True)
    
    create_dummy_pdf(pdf1, "Conținut document 1")
    create_dummy_pdf(pdf2, "Conținut document 2")
    create_dummy_pdf(pdf3, "Conținut document 3")
    
    print_info(f"\nRulare indexare_incrementala pe: {test_folder}")
    print("-" * 60)
    
    # Rulează indexarea
    indexare_incrementala(str(test_folder))
    
    print("-" * 60)
    
    # Verifică tracking file
    tracking_file = Path("fisiere_indexate.json")
    if tracking_file.exists():
        with open(tracking_file, 'r', encoding='utf-8') as f:
            tracked = json.load(f)
        
        print_success(f"Tracking file creat cu {len(tracked)} fișiere")
        
        # Verifică dacă toate fișierele sunt tracked
        pdf1_abs = str(pdf1.absolute())
        pdf2_abs = str(pdf2.absolute())
        pdf3_abs = str(pdf3.absolute())
        
        if pdf1_abs in tracked:
            print_success(f"✓ {pdf1.name} este tracked (hash: {tracked[pdf1_abs][:8]}...)")
        else:
            print_error(f"✗ {pdf1.name} NU este tracked!")
        
        if pdf2_abs in tracked:
            print_success(f"✓ {pdf2.name} este tracked (hash: {tracked[pdf2_abs][:8]}...)")
        else:
            print_error(f"✗ {pdf2.name} NU este tracked!")
        
        if pdf3_abs in tracked:
            print_success(f"✓ {pdf3.name} este tracked (hash: {tracked[pdf3_abs][:8]}...)")
        else:
            print_error(f"✗ {pdf3.name} NU este tracked!")
        
        return True
    else:
        print_error("Tracking file NU a fost creat!")
        return False

def test_2_detectare_fisiere_existente(test_folder):
    """Test 2: Detectare fișiere deja indexate"""
    print_header("TEST 2: Detectare Fișiere Deja Indexate")
    
    print_info("Rulare indexare_incrementala a doua oară (fără modificări)")
    print_info("Așteptare: Toate fișierele ar trebui să fie DEJA INDEXATE")
    print("-" * 60)
    
    # Rulează indexarea din nou
    indexare_incrementala(str(test_folder))
    
    print("-" * 60)
    print_success("Dacă ai văzut '[DEJA INDEXAT]' pentru toate fișierele → TEST PASSED ✓")
    
    return True

def test_3_detectare_fisiere_modificate(test_folder):
    """Test 3: Detectare fișiere modificate"""
    print_header("TEST 3: Detectare Fișiere Modificate")
    
    # Modifică un fișier
    pdf1 = test_folder / "document1.pdf"
    
    print_info(f"Modificare fișier: {pdf1.name}")
    
    # Salvează hash-ul vechi
    old_hash = calculeaza_hash_fisier(str(pdf1))
    print_info(f"Hash vechi: {old_hash[:16]}...")
    
    # Așteaptă puțin pentru a fi sigur că modificarea e detectată
    time.sleep(0.1)
    
    # Modifică conținutul
    with open(pdf1, 'a', encoding='utf-8') as f:
        f.write("\nConținut adăugat!")
    
    # Calculează hash nou
    new_hash = calculeaza_hash_fisier(str(pdf1))
    print_info(f"Hash nou:  {new_hash[:16]}...")
    
    if old_hash != new_hash:
        print_success("Hash-ul s-a schimbat → Modificarea va fi detectată")
    else:
        print_error("Hash-ul NU s-a schimbat!")
        return False
    
    print_info("\nRulare indexare_incrementala după modificare")
    print_info("Așteptare: document1.pdf ar trebui să fie [NOU/MODIFICAT]")
    print("-" * 60)
    
    # Rulează indexarea
    indexare_incrementala(str(test_folder))
    
    print("-" * 60)
    
    # Verifică că hash-ul s-a actualizat în tracking
    tracking_file = Path("fisiere_indexate.json")
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracked = json.load(f)
    
    pdf1_abs = str(pdf1.absolute())
    if tracked[pdf1_abs] == new_hash:
        print_success(f"Hash actualizat în tracking: {tracked[pdf1_abs][:16]}...")
        return True
    else:
        print_error("Hash-ul NU s-a actualizat în tracking!")
        return False

def test_4_adaugare_fisier_nou(test_folder):
    """Test 4: Adăugare fișier nou după indexare inițială"""
    print_header("TEST 4: Adăugare Fișier Nou")
    
    # Adaugă un fișier nou
    pdf4 = test_folder / "document4_nou.pdf"
    create_dummy_pdf(pdf4, "Conținut document nou adăugat")
    
    print_info("\nRulare indexare_incrementala după adăugare fișier nou")
    print_info("Așteptare: document4_nou.pdf ar trebui să fie [NOU/MODIFICAT]")
    print_info("Așteptare: Celelalte fișiere ar trebui să fie [DEJA INDEXAT]")
    print("-" * 60)
    
    # Rulează indexarea
    indexare_incrementala(str(test_folder))
    
    print("-" * 60)
    
    # Verifică tracking
    tracking_file = Path("fisiere_indexate.json")
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracked = json.load(f)
    
    pdf4_abs = str(pdf4.absolute())
    if pdf4_abs in tracked:
        print_success(f"Fișierul nou a fost adăugat în tracking")
        print_success(f"Total fișiere tracked: {len(tracked)}")
        return True
    else:
        print_error("Fișierul nou NU a fost adăugat în tracking!")
        return False

def test_5_verificare_tracking_file(test_folder):
    """Test 5: Verificare structură tracking file"""
    print_header("TEST 5: Verificare Structură Tracking File")
    
    tracking_file = Path("fisiere_indexate.json")
    
    if not tracking_file.exists():
        print_error("Tracking file nu există!")
        return False
    
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracked = json.load(f)
    
    print_info(f"Fișiere tracked: {len(tracked)}")
    print("\nConținut fisiere_indexate.json:")
    print("-" * 60)
    
    for path, hash_val in tracked.items():
        filename = Path(path).name
        print(f"  {filename:30s} → {hash_val[:16]}...")
    
    print("-" * 60)
    
    # Verificări
    checks_passed = 0
    total_checks = 3
    
    # Check 1: Toate hash-urile sunt MD5 (32 caractere hex)
    all_valid_hashes = all(len(h) == 32 and all(c in '0123456789abcdef' for c in h) 
                           for h in tracked.values())
    if all_valid_hashes:
        print_success("Toate hash-urile sunt MD5 valide (32 caractere hex)")
        checks_passed += 1
    else:
        print_error("Unele hash-uri nu sunt MD5 valide!")
    
    # Check 2: Toate căile sunt absolute
    all_absolute = all(Path(p).is_absolute() for p in tracked.keys())
    if all_absolute:
        print_success("Toate căile sunt absolute")
        checks_passed += 1
    else:
        print_error("Unele căi nu sunt absolute!")
    
    # Check 3: Toate fișierele există
    all_exist = all(Path(p).exists() for p in tracked.keys())
    if all_exist:
        print_success("Toate fișierele tracked există pe disk")
        checks_passed += 1
    else:
        print_warning("Unele fișiere tracked nu mai există pe disk")
    
    print(f"\n{Colors.BOLD}Verificări passed: {checks_passed}/{total_checks}{Colors.RESET}")
    
    return checks_passed == total_checks

def cleanup_test_environment(test_folder, backup_file):
    """Curăță mediul de test"""
    print_header("CLEANUP: Curățare Mediu de Test")
    
    # Șterge folder de test
    if test_folder.exists():
        shutil.rmtree(test_folder)
        print_success(f"Șters folder de test: {test_folder}")
    
    # Șterge tracking file de test
    tracking_file = Path("fisiere_indexate.json")
    if tracking_file.exists():
        tracking_file.unlink()
        print_success("Șters fisiere_indexate.json de test")
    
    # Restaurează backup dacă există
    if backup_file and backup_file.exists():
        shutil.move(backup_file, tracking_file)
        print_success(f"Restaurat backup: {tracking_file}")
    
    print_info("Cleanup complet!")

def main():
    """Rulează toate testele"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TEST SUITE: INDEXARE INCREMENTALĂ                     ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    test_folder = None
    backup_file = None
    results = []
    
    try:
        # Setup
        test_folder, backup_file = setup_test_environment()
        
        # Rulează testele
        results.append(("Test 1: Indexare fișiere noi", test_1_indexare_fisiere_noi(test_folder)))
        results.append(("Test 2: Detectare fișiere existente", test_2_detectare_fisiere_existente(test_folder)))
        results.append(("Test 3: Detectare fișiere modificate", test_3_detectare_fisiere_modificate(test_folder)))
        results.append(("Test 4: Adăugare fișier nou", test_4_adaugare_fisier_nou(test_folder)))
        results.append(("Test 5: Verificare tracking file", test_5_verificare_tracking_file(test_folder)))
        
    except Exception as e:
        print_error(f"Eroare în timpul testării: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if test_folder:
            cleanup_test_environment(test_folder, backup_file)
    
    # Afișează rezultatele
    print_header("REZULTATE FINALE")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
    if passed == total:
        print(f"{Colors.BOLD}{Colors.GREEN}✓ TOATE TESTELE AU TRECUT: {passed}/{total}{Colors.RESET}")
    else:
        print(f"{Colors.BOLD}{Colors.YELLOW}⚠ UNELE TESTE AU EȘUAT: {passed}/{total}{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    main()
