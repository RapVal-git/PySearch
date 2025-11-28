import time
import os
import schedule
from indexare_incrementala import indexare_incrementala
import config
# Citește calea din variabilă de mediu
FOLDER_PDF = config.DEFAULT_INDEXING_FOLDER

def job():
    """Functie care ruleaza indexarea incrementala"""
    print("\n" + "="*60)
    print(f"START indexare automata: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    try:
        indexare_incrementala(FOLDER_PDF)
    except Exception as e:
        print(f"EROARE la indexare: {e}")
    
    print("\n" + "="*60)
    print(f"FINAL indexare automata: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("Serviciu de indexare automata pornit!")
    print(f"Folder monitorizat: {FOLDER_PDF}")
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
