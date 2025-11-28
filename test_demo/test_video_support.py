"""
Script de testare pentru suportul VIDEO (Whisper)
"""
import os
import sys

def check_dependencies():
    print("="*60)
    print("VERIFICARE DEPENDENȚE")
    print("="*60)
    
    try:
        import whisper
        import torch
        print(f"✅ openai-whisper instalat (v{whisper.__version__})")
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"ℹ️  Device disponibil: {device.upper()}")
        
        if device == "cpu":
            print("⚠️  ATENȚIE: Rularea pe CPU va fi lentă pentru video-uri lungi.")
            
    except ImportError as e:
        print(f"❌ Eroare import whisper: {e}")
        return False

    try:
        from moviepy.editor import VideoFileClip
        print("✅ moviepy instalat")
    except ImportError as e:
        print(f"❌ Eroare import moviepy: {e}")
        return False
        
    return True

def test_transcription():
    print("\n" + "="*60)
    print("TEST TRANSCRIERE")
    print("="*60)
    
    # Căutăm un fișier video de test
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav')
    test_file = None
    
    for file in os.listdir('.'):
        if file.lower().endswith(video_extensions):
            test_file = file
            break
            
    if not test_file:
        print("❌ Nu s-a găsit niciun fișier video/audio în folderul curent.")
        print("💡 Te rog copiază un fișier video scurt (ex: test.mp4) aici pentru testare.")
        return
        
    print(f"📄 Fișier test găsit: {test_file}")
    
    from video_extractie import extrage_text_video
    
    try:
        print("🚀 Începere transcriere (model 'base')...")
        count = 0
        for timestamp, text in extrage_text_video(test_file, model_size="base"):
            count += 1
            print(f"\n[{timestamp}] {text}")
            
            if count >= 3:
                print("\n... (oprit după 3 segmente pentru test)")
                break
                
        if count > 0:
            print("\n✅ Transcriere reușită!")
        else:
            print("\n⚠️  Nu s-a extras niciun text (posibil audio gol sau muzică?)")
            
    except Exception as e:
        print(f"\n❌ Eroare la transcriere: {e}")

if __name__ == "__main__":
    if check_dependencies():
        test_transcription()
