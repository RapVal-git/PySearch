import time
import os
import schedule
from indexare_incrementala import indexare_incrementala
import config

# Foldere de indexare (prioritate: override din env, apoi lista din config)
if config.DEFAULT_INDEXING_FOLDER:
    FOLDERS = [config.DEFAULT_INDEXING_FOLDER]
else:
    FOLDERS = [f for f in getattr(config, "INDEXING_FOLDERS", []) if f]

def job():
    """Functie care ruleaza indexarea incrementala"""
    print("\n" + "="*60)
    print(f"START indexare automata: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        for folder in FOLDERS:
            print(f"Folder tinta: {folder}")
            indexare_incrementala(folder)
    except Exception as e:
        print(f"EROARE la indexare: {e}")
    
    print("\n" + "="*60)
    print(f"FINAL indexare automata: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    if not FOLDERS:
        print("Eroare: nu exista foldere configurate pentru indexare.")
        raise SystemExit(1)

    print("Serviciu de indexare automata pornit!")
    print(f"Foldere monitorizate: {', '.join(FOLDERS)}")
    print("Verifica folderul la fiecare 1 ora pentru fisiere noi...")
    print("Apasa Ctrl+C pentru a opri.\n")
    
    # Ruleaza imediat la pornire
    job()
    
    # Programeaza sa ruleze la fiecare ora
    schedule.every(1).hours.do(job)
    
    # Loop infinit
    while True:
        schedule.run_pending()
        time.sleep(60)  # Verifica la fiecare minut daca e timpul
