"""
Script pentru instalarea PyTorch cu suport CUDA
"""
import subprocess
import sys

print("="*70)
print("INSTALARE PYTORCH CU SUPORT CUDA PENTRU WHISPER")
print("="*70)

print("\n📋 Pași pentru activarea GPU:")
print("\n1. Verifică că ai driverele NVIDIA instalate")
print("   - Caută în Start: 'NVIDIA Control Panel'")
print("   - Sau rulează: C:\\Windows\\System32\\nvidia-smi.exe")

print("\n2. Dezinstalează PyTorch actual (fără CUDA):")
print("   pip uninstall torch torchvision torchaudio")

print("\n3. Instalează PyTorch cu CUDA:")
print("\n   Pentru CUDA 11.8 (recomandat pentru majoritatea GPU-urilor):")
print("   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

print("\n   Pentru CUDA 12.1 (GPU-uri mai noi):")
print("   pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

print("\n" + "="*70)
response = input("\nVrei să instalez automat PyTorch cu CUDA 11.8? (da/nu): ").strip().lower()

if response == "da":
    print("\n🚀 Dezinstalare PyTorch actual...")
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"])
    
    print("\n🚀 Instalare PyTorch cu CUDA 11.8...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", 
        "torch", "torchvision", "torchaudio",
        "--index-url", "https://download.pytorch.org/whl/cu118"
    ])
    
    print("\n✅ Instalare completă!")
    print("\n🔍 Verificare GPU...")
    
    import torch
    print(f"\nCUDA disponibil: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU detectat: {torch.cuda.get_device_name(0)}")
        print("🎉 GPU activat cu succes!")
    else:
        print("⚠️  GPU încă nu este detectat. Posibile cauze:")
        print("  - Driverele NVIDIA nu sunt instalate")
        print("  - Versiunea CUDA incompatibilă")
        print("  - Repornire necesară după instalare drivere")
else:
    print("\n❌ Instalare anulată. Rulează manual comenzile de mai sus.")
