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

# Variabilă globală pentru a cache-ui modelul și a nu-l reîncărca la fiecare video
_GLOBAL_WHISPER_MODEL = None
_CURRENT_MODEL_SIZE = None

def get_whisper_model(model_size):
    """Gestionează instanța globală a modelului Whisper"""
    global _GLOBAL_WHISPER_MODEL, _CURRENT_MODEL_SIZE
    
    # Dacă avem deja modelul încărcat cu aceeași dimensiune, îl returnăm
    if _GLOBAL_WHISPER_MODEL is not None and _CURRENT_MODEL_SIZE == model_size:
        return _GLOBAL_WHISPER_MODEL
    
    # Dacă avem un model încărcat dar vrem altă dimensiune, sau nu avem deloc
    if _GLOBAL_WHISPER_MODEL is not None:
        print(f"   -> Eliberare model anterior ({_CURRENT_MODEL_SIZE})...")
        del _GLOBAL_WHISPER_MODEL
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    print(f"   -> Încărcare model Faster Whisper '{model_size}' (o singură dată)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    print(f"   -> Rulează pe: {device.upper()} (Compute: {compute_type})")
    
    _GLOBAL_WHISPER_MODEL = WhisperModel(model_size, device=device, compute_type=compute_type)
    _CURRENT_MODEL_SIZE = model_size
    return _GLOBAL_WHISPER_MODEL

def extrage_text_video(cale_video, model_size=None):
    """
    Extrage audio din video și îl transcrie folosind Faster Whisper (CTranslate2).
    """
    if model_size is None:
        model_size = config.WHISPER_MODEL_SIZE
        
    if not os.path.isfile(cale_video):
        print(f"Eroare: Fisierul {cale_video} nu exista.")
        return

    print(f"Procesare Video: {os.path.basename(cale_video)}")
    
    temp_audio_path = None
    video = None
    
    try:
        # 1. Extragere Audio
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio:
            temp_audio_path = temp_audio.name
        
        print("   -> Extragere audio...")
        video = VideoFileClip(cale_video)
        video.audio.write_audiofile(temp_audio_path, logger=None)
        
        # ÎNCHIDEM EXPLICIT VIDEO PENTRU A ELIBERA FIȘIERUL
        video.close()
        del video
        video = None
        
    except Exception as e:
        print(f"Eroare la extragerea audio: {e}")
        if video:
            try: video.close()
            except: pass
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        return

    # 2. Transcriere
    try:
        # Folosim funcția de caching
        model = get_whisper_model(model_size)
        
        print("   -> Transcriere în curs (poate dura)...")
        segments, info = model.transcribe(temp_audio_path, beam_size=config.WHISPER_BEAM_SIZE)
        
        print(f"   -> Limba detectată: {info.language} (probabilitate: {info.language_probability:.2f})")
        
        # 3. Yield segmente
        current_text_block = []
        current_start_time = 0
        block_duration_threshold = config.VIDEO_BLOCK_DURATION
        
        for segment in segments:
            start = segment.start
            end = segment.end
            text = segment.text
            
            if not current_text_block:
                current_start_time = start
            
            current_text_block.append(text)
            
            if (end - current_start_time >= block_duration_threshold):
                time_str = f"{int(current_start_time // 60):02d}:{int(current_start_time % 60):02d}"
                full_text = "".join(current_text_block)
                yield (time_str, full_text)
                current_text_block = []
        
        if current_text_block:
            time_str = f"{int(current_start_time // 60):02d}:{int(current_start_time % 60):02d}"
            full_text = "".join(current_text_block)
            yield (time_str, full_text)
            
        print("   -> Transcriere finalizată!")

    except Exception as e:
        print(f"Eroare la transcriere: {e}")
        raise
    finally:
        # Curățenie fișier temporar
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except:
                pass

if __name__ == "__main__":
    # Test
    print("Acest modul necesită un fișier video pentru testare.")
