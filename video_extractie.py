import os
import site
import config

# Fix pentru erorile de DLL ctranslate2 (cublas64_12.dll not found)
# Încercăm să adăugăm căile bibliotecilor nvidia instalate via pip
# Fix pentru erorile de DLL ctranslate2 (cublas64_12.dll not found)
# Încercăm să adăugăm căile bibliotecilor nvidia instalate via pip
# ACEST BLOC TREBUIE SĂ FIE PRIMUL, înainte de orice import care folosește ctranslate2
try:
    site_packages = site.getsitepackages()[0]
    if "site-packages" not in site_packages:
        # Fallback for some venv configurations
        for path in site.getsitepackages():
            if "site-packages" in path:
                site_packages = path
                break
    
    nvidia_cublas_path = os.path.join(site_packages, "nvidia", "cublas", "bin")
    nvidia_cudnn_path = os.path.join(site_packages, "nvidia", "cudnn", "bin")
    
    if os.path.exists(nvidia_cublas_path):
        os.add_dll_directory(nvidia_cublas_path)
        os.environ["PATH"] += os.pathsep + nvidia_cublas_path
        
    if os.path.exists(nvidia_cudnn_path):
        os.add_dll_directory(nvidia_cudnn_path)
        os.environ["PATH"] += os.pathsep + nvidia_cudnn_path

except Exception as e:
    print(f"Warning: Could not add nvidia libraries to DLL path: {e}")

from faster_whisper import WhisperModel
import tempfile
from moviepy import VideoFileClip
import torch
import imageio_ffmpeg

# Adăugăm ffmpeg din imageio_ffmpeg în PATH pentru ca Whisper să îl găsească
os.environ["PATH"] += os.pathsep + os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

def extrage_text_video(cale_video, model_size=None):
    """
    Extrage audio din video și îl transcrie folosind Faster Whisper (CTranslate2).
    
    Args:
        cale_video: Calea către fișierul video
        model_size: Dimensiunea modelului Whisper (None = folosește din config.py)
        
    Yields:
        Tuple (timestamp_start, text_segment)
        Simulăm "pagini" bazate pe timp (ex: segmente de transcriere)
    """
    if model_size is None:
        model_size = config.WHISPER_MODEL_SIZE
    if not os.path.isfile(cale_video):
        print(f"Eroare: Fisierul {cale_video} nu exista.")
        return

    print(f"Procesare Video: {os.path.basename(cale_video)}")
    
    # 1. Extragere Audio
    try:
        # Folosim un fișier temporar pentru audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        print("   -> Extragere audio...")
        video = VideoFileClip(cale_video)
        # Extragem doar audio, fără verbose output
        video.audio.write_audiofile(temp_audio_path, logger=None)
        video.close()
        
    except Exception as e:
        print(f"Eroare la extragerea audio: {e}")
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return

    # 2. Transcriere cu Faster Whisper
    try:
        print(f"   -> Încărcare model Faster Whisper '{model_size}'...")
        # Verificăm dacă avem GPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        print(f"   -> Rulează pe: {device.upper()} (Compute: {compute_type})")
        
        model = WhisperModel(model_size, device=device, compute_type=compute_type)
        
        print("   -> Transcriere în curs (poate dura)...")
        # beam_size=5 este o valoare comună pentru acuratețe
        segments, info = model.transcribe(temp_audio_path, beam_size=5)
        
        print(f"   -> Limba detectată: {info.language} (probabilitate: {info.language_probability:.2f})")
        
        # 3. Yield segmente
        
        # Grupăm segmentele pentru a nu avea chunk-uri prea mici
        current_text_block = []
        current_start_time = 0
        block_duration_threshold = config.VIDEO_BLOCK_DURATION  # din config.py
        
        # segments este un generator, deci transcrierea se întâmplă pe măsură ce iterăm
        for segment in segments:
            start = segment.start
            end = segment.end
            text = segment.text
            
            if not current_text_block:
                current_start_time = start
            
            current_text_block.append(text)
            
            # Dacă blocul curent depășește durata
            if (end - current_start_time >= block_duration_threshold):
                # Formatăm timpul ca MM:SS
                time_str = f"{int(current_start_time // 60):02d}:{int(current_start_time % 60):02d}"
                full_text = "".join(current_text_block)
                
                yield (time_str, full_text)
                
                current_text_block = []
        
        # Yield ultimul bloc dacă există
        if current_text_block:
            time_str = f"{int(current_start_time // 60):02d}:{int(current_start_time % 60):02d}"
            full_text = "".join(current_text_block)
            yield (time_str, full_text)
            
        print("   -> Transcriere finalizată!")

    except Exception as e:
        print(f"Eroare la transcriere: {e}")
    finally:
        # Curățenie
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except:
                pass

if __name__ == "__main__":
    # Test
    print("Acest modul necesită un fișier video pentru testare.")
