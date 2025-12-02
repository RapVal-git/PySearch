"""
Script de test pentru a reproduce problema de indexare video
"""
import os
import sys

# Adaugă calea curentă pentru a importa modulele
sys.path.insert(0, os.path.dirname(__file__))

from procesare_text import iterare_chunkuri_video

def test_video_processing(cale_video):
    """Testează procesarea unui video și afișează eventualele erori"""
    print(f"=== Test Procesare Video ===")
    print(f"Fișier: {cale_video}")
    print(f"Există: {os.path.exists(cale_video)}")
    print()
    
    if not os.path.exists(cale_video):
        print("EROARE: Fișierul nu există!")
        return
    
    try:
        chunk_count = 0
        for item in iterare_chunkuri_video(cale_video):
            chunk_count += 1
            text = item.get('text_chunk', '')
            metadata = item.get('metadata', {})
            
            print(f"Chunk {chunk_count}:")
            print(f"  Timestamp: {metadata.get('pagina', 'N/A')}")
            print(f"  Text length: {len(text)} caractere")
            print(f"  Preview: {text[:100]}...")
            print()
        
        print(f"✅ Procesare completă! Total chunk-uri: {chunk_count}")
        
    except Exception as e:
        print(f"❌ EROARE la procesare:")
        print(f"   Tip: {type(e).__name__}")
        print(f"   Mesaj: {e}")
        import traceback
        print("\nStack trace complet:")
        traceback.print_exc()

if __name__ == "__main__":
    # Permite utilizatorului să specifice calea video
    if len(sys.argv) > 1:
        cale_video = sys.argv[1]
    else:
        cale_video = input("Introdu calea către fișierul video: ").strip()
    
    test_video_processing(cale_video)
