"""
Test Manual Simplu pentru Indexare Incrementală

Acest script te ghidează pas cu pas prin testarea funcționalității
de tracking și indexare incrementală.
"""

import os
import json
from pathlib import Path
from indexare_incrementala import calculeaza_hash_fisier

def print_separator():
    print("\n" + "="*70 + "\n")

def show_tracking_status():
    """Afișează statusul curent al tracking-ului"""
    tracking_file = Path("fisiere_indexate.json")
    
    print_separator()
    print("📊 STATUS TRACKING CURENT")
    print_separator()
    
    if not tracking_file.exists():
        print("❌ Fișierul fisiere_indexate.json NU există încă")
        print("   → Niciun fișier nu a fost indexat")
        return {}
    
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracked = json.load(f)
    
    if not tracked:
        print("⚠️  Fișierul fisiere_indexate.json este gol")
        return {}
    
    print(f"✅ Total fișiere tracked: {len(tracked)}")
    print("\nLista fișiere indexate:")
    print("-" * 70)
    
    for i, (path, hash_val) in enumerate(tracked.items(), 1):
        filename = Path(path).name
        exists = "✓" if Path(path).exists() else "✗ (LIPSĂ)"
        print(f"{i:2d}. {filename:40s} {exists}")
        print(f"    Cale: {path}")
        print(f"    Hash: {hash_val}")
        print()
    
    return tracked

def check_file_status(file_path):
    """Verifică statusul unui fișier specific"""
    tracking_file = Path("fisiere_indexate.json")
    
    print_separator()
    print(f"🔍 VERIFICARE FIȘIER: {Path(file_path).name}")
    print_separator()
    
    if not Path(file_path).exists():
        print(f"❌ Fișierul nu există: {file_path}")
        return
    
    # Calculează hash curent
    current_hash = calculeaza_hash_fisier(file_path)
    print(f"Hash curent: {current_hash}")
    
    # Verifică în tracking
    if not tracking_file.exists():
        print("\n❌ Fișierul fisiere_indexate.json nu există")
        print("   → Fișierul NU este indexat")
        return
    
    with open(tracking_file, 'r', encoding='utf-8') as f:
        tracked = json.load(f)
    
    abs_path = str(Path(file_path).absolute())
    
    if abs_path not in tracked:
        print("\n❌ Fișierul NU este în tracking")
        print("   → Fișierul va fi indexat ca NOU")
    else:
        tracked_hash = tracked[abs_path]
        print(f"\n✅ Fișierul ESTE în tracking")
        print(f"   Hash tracked: {tracked_hash}")
        
        if current_hash == tracked_hash:
            print("\n✅ Hash-urile COINCID")
            print("   → Fișierul va fi SĂRIT (deja indexat)")
        else:
            print("\n⚠️  Hash-urile DIFERĂ")
            print("   → Fișierul va fi REINDEXAT (modificat)")

def interactive_menu():
    """Meniu interactiv pentru testare"""
    while True:
        print_separator()
        print("🧪 TEST MANUAL - INDEXARE INCREMENTALĂ")
        print_separator()
        print("Opțiuni:")
        print("  1. Afișează status tracking curent")
        print("  2. Verifică un fișier specific")
        print("  3. Compară două fișiere")
        print("  4. Simulează modificare fișier")
        print("  5. Afișează conținut fisiere_indexate.json (raw)")
        print("  0. Ieșire")
        print()
        
        choice = input("Alege opțiune (0-5): ").strip()
        
        if choice == "0":
            print("\n👋 La revedere!")
            break
        
        elif choice == "1":
            show_tracking_status()
            input("\nApasă Enter pentru a continua...")
        
        elif choice == "2":
            file_path = input("\nIntroduceți calea către fișier: ").strip()
            if file_path:
                check_file_status(file_path)
            input("\nApasă Enter pentru a continua...")
        
        elif choice == "3":
            file1 = input("\nFișier 1: ").strip()
            file2 = input("Fișier 2: ").strip()
            
            if file1 and file2 and Path(file1).exists() and Path(file2).exists():
                hash1 = calculeaza_hash_fisier(file1)
                hash2 = calculeaza_hash_fisier(file2)
                
                print_separator()
                print("📊 COMPARARE FIȘIERE")
                print_separator()
                print(f"Fișier 1: {Path(file1).name}")
                print(f"  Hash: {hash1}")
                print()
                print(f"Fișier 2: {Path(file2).name}")
                print(f"  Hash: {hash2}")
                print()
                
                if hash1 == hash2:
                    print("✅ Fișierele sunt IDENTICE")
                else:
                    print("⚠️  Fișierele sunt DIFERITE")
            else:
                print("❌ Unul sau ambele fișiere nu există!")
            
            input("\nApasă Enter pentru a continua...")
        
        elif choice == "4":
            file_path = input("\nIntroduceți calea către fișier: ").strip()
            
            if not file_path or not Path(file_path).exists():
                print("❌ Fișierul nu există!")
                input("\nApasă Enter pentru a continua...")
                continue
            
            # Afișează hash înainte
            hash_before = calculeaza_hash_fisier(file_path)
            print(f"\nHash ÎNAINTE: {hash_before}")
            
            # Adaugă text
            text_to_add = input("\nText de adăugat (Enter pentru text default): ").strip()
            if not text_to_add:
                text_to_add = "\n<!-- Modificare test -->"
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(text_to_add)
            
            # Afișează hash după
            hash_after = calculeaza_hash_fisier(file_path)
            print(f"Hash DUPĂ:   {hash_after}")
            
            if hash_before != hash_after:
                print("\n✅ Fișierul a fost modificat cu succes!")
                print("   → La următoarea indexare va fi detectat ca MODIFICAT")
            else:
                print("\n⚠️  Hash-ul nu s-a schimbat (neașteptat)")
            
            input("\nApasă Enter pentru a continua...")
        
        elif choice == "5":
            tracking_file = Path("fisiere_indexate.json")
            
            print_separator()
            print("📄 CONȚINUT RAW: fisiere_indexate.json")
            print_separator()
            
            if not tracking_file.exists():
                print("❌ Fișierul nu există")
            else:
                with open(tracking_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(content)
            
            input("\nApasă Enter pentru a continua...")
        
        else:
            print("\n❌ Opțiune invalidă!")
            input("\nApasă Enter pentru a continua...")

if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║        TEST MANUAL - INDEXARE INCREMENTALĂ                        ║
║                                                                    ║
║  Acest tool te ajută să verifici funcționalitatea de tracking     ║
║  și să înțelegi cum funcționează indexarea incrementală.          ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    interactive_menu()
