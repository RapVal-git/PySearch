"""
Script pentru verificarea suportului GPU pentru Whisper
"""
import torch

print("="*60)
print("VERIFICARE SUPORT GPU")
print("="*60)

print(f"\nVersiune PyTorch: {torch.__version__}")
print(f"CUDA disponibil: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Versiune CUDA: {torch.version.cuda}")
    print(f"Număr GPU-uri: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
else:
    print("\n❌ CUDA nu este disponibil!")
    print("\n💡 Soluție:")
    print("Trebuie să instalezi PyTorch cu suport CUDA.")
    print("\nPentru CUDA 11.8:")
    print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("\nPentru CUDA 12.1:")
    print("pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")
    print("\nVerifică versiunea CUDA instalată pe sistem cu: nvidia-smi")
