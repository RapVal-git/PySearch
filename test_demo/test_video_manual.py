import os
import sys
from video_extractie import extrage_text_video

def main():
    print("="*60)
    print("🎥 TESTARE MANUALĂ TRANSCRIERE VIDEO")
    print("="*60)
    
    # 1. Obține calea fișierului
    if len(sys.argv) > 1:
        cale_video = sys.argv[1]
    else:
        cale_video = input("\nIntrodu calea completă către fișierul video: ").strip()
        # Elimină ghilimelele dacă există (copy-paste path)
        cale_video = cale_video.strip('"').strip("'")
    
    # 2. Verifică dacă fișierul există
    if not os.path.exists(cale_video):
        print(f"\n❌ Eroare: Fișierul nu a fost găsit la calea:\n{cale_video}")
        return

    print(f"\n📄 Fișier selectat: {cale_video}")
    
    # 3. Alege modelul (opțional)
    print("\nModele disponibile: tiny, base, small, medium, large")
    model = input("Alege modelul Whisper (default 'base'): ").strip()
    if not model:
        model = "base"
        
    # 4. Pregătire fișier ieșire
    nume_video = os.path.basename(cale_video)
    nume_txt = os.path.splitext(nume_video)[0] + "_transcript.txt"
    cale_txt = os.path.join(os.path.dirname(cale_video), nume_txt)
    
    # 5. Procesare
    print(f"\n🚀 Începere transcriere (Model: {model})...")
    print(f"💾 Rezultatul va fi salvat în: {nume_txt}")
    print("⏳ Te rog așteaptă, poate dura câteva minute pe CPU...\n")
    
    try:
        with open(cale_txt, "w", encoding="utf-8") as f:
            f.write(f"Transcript pentru: {nume_video}\n")
            f.write("=" * 50 + "\n\n")
            
            count = 0
            for timestamp, text in extrage_text_video(cale_video, model_size=model):
                count += 1
                
                # Afișare în consolă
                print(f"[{timestamp}] {text}")
                print("-" * 40)
                
                # Scriere în fișier
                f.write(f"[{timestamp}]\n{text}\n\n")
                f.flush() # Asigură scrierea pe disc
            
        if count > 0:
            print(f"\n✅ Transcriere finalizată cu succes! ({count} segmente)")
            print(f"📄 Fișier salvat: {cale_txt}")
        else:
            print("\n⚠️  Nu s-a extras niciun text.")
            
    except Exception as e:
        print(f"\n❌ Eroare critică: {e}")
    
    input("\nApasă Enter pentru a ieși...")

if __name__ == "__main__":
    main()
