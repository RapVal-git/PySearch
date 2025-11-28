"""
Script de testare pentru verificarea procesării în memorie (fără fișiere TXT)
"""
import os
from procesare_text import iterare_chunkuri_document

def test_procesare_fara_txt():
    """Testează că procesarea funcționează fără a crea fișiere TXT"""
    
    print("="*60)
    print("TEST: Procesare în memorie (fără fișiere TXT)")
    print("="*60)
    
    # Găsește un PDF de test
    test_files = []
    
    # Caută în directorul curent
    for file in os.listdir('.'):
        if file.lower().endswith(('.pdf', '.docx')):
            test_files.append(file)
            if len(test_files) >= 2:  # Testăm max 2 fișiere
                break
    
    if not test_files:
        print("❌ Nu s-au găsit fișiere PDF sau DOCX pentru testare")
        print("💡 Copiază un fișier PDF sau DOCX în directorul curent")
        return False
    
    success = True
    
    for test_file in test_files:
        print(f"\n📄 Testare: {test_file}")
        print("-" * 60)
        
        # Verifică că nu există fișier TXT înainte
        txt_file = os.path.splitext(test_file)[0] + ".txt"
        txt_existed_before = os.path.exists(txt_file)
        
        try:
            chunk_count = 0
            for item in iterare_chunkuri_document(test_file):
                chunk_count += 1
                
                # Afișează primele 2 chunk-uri
                if chunk_count <= 2:
                    print(f"\nChunk {chunk_count}:")
                    print(f"  Tip: {item['metadata']['tip_document']}")
                    print(f"  Pagină: {item['metadata']['pagina']}")
                    print(f"  Lungime text: {len(item['text_chunk'])} caractere")
                    print(f"  Preview: {item['text_chunk'][:100]}...")
            
            print(f"\n✅ Total chunk-uri procesate: {chunk_count}")
            
            # Verifică că NU s-a creat fișier TXT nou
            txt_exists_after = os.path.exists(txt_file)
            
            if not txt_existed_before and txt_exists_after:
                print(f"❌ EROARE: S-a creat fișier TXT intermediar: {txt_file}")
                success = False
            else:
                print(f"✅ Nu s-a creat fișier TXT intermediar")
                
        except Exception as e:
            print(f"❌ Eroare la procesare: {e}")
            import traceback
            traceback.print_exc()
            success = False
    
    return success


if __name__ == "__main__":
    print("\n🧪 TESTARE PROCESARE ÎN MEMORIE\n")
    
    result = test_procesare_fara_txt()
    
    print("\n" + "="*60)
    print("📊 REZULTAT")
    print("="*60)
    
    if result:
        print("🎉 TEST TRECUT!")
        print("\n✅ Avantaje:")
        print("  • Nu se mai creează fișiere TXT intermediare")
        print("  • Economisește spațiu pe disc")
        print("  • Procesare mai rapidă (fără I/O pe disc)")
        print("  • Ideal pentru arhive mari (8 TB)")
    else:
        print("❌ TEST EȘUAT!")
        print("Verifică erorile de mai sus")
