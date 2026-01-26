import subprocess
import sys
import os

def run_command(command):
    print(f"Running: {' '.join(command)}")
    try:
        subprocess.check_call(command)
        print("Success!")
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        sys.exit(1)

print("=== Fixing GPU Dependencies ===")

# 1. Uninstall existing torch packages
print("\n1. Uninstalling existing torch packages...")
run_command([sys.executable, "-m", "pip", "uninstall", "-y", "torch", "torchvision", "torchaudio"])

# 2. Install PyTorch with CUDA 12.1 support (compatible with most modern GPUs and Python 3.13 if supported)
# Using --pre might be needed for 3.13 if stable isn't out, but let's try stable first or the one from the index.
# PyTorch 2.5.0 supports Python 3.13.
print("\n2. Installing PyTorch with CUDA 12.1 support...")
run_command([
    sys.executable, "-m", "pip", "install", 
    "torch", "torchvision", "torchaudio", 
    "--index-url", "https://download.pytorch.org/whl/cu121"
])

# 3. Install NVIDIA libraries required by CTranslate2/Faster-Whisper
print("\n3. Installing NVIDIA libraries...")
run_command([
    sys.executable, "-m", "pip", "install", 
    "nvidia-cublas-cu12", "nvidia-cudnn-cu12"
])

print("\n=== Verification ===")
import torch
print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
else:
    print("WARNING: CUDA is still not available.")

print("\nDone.")
