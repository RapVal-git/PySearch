import torch
import os
import sys

print(f"Python version: {sys.version}")
print(f"Torch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print(f"CUDA current device: {torch.cuda.current_device()}")
    print(f"CUDA device name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA is NOT available.")

try:
    import ctranslate2
    print(f"CTranslate2 version: {ctranslate2.__version__}")
except ImportError:
    print("CTranslate2 not installed.")

# Check for nvidia libraries in site-packages
import site
try:
    site_packages = site.getsitepackages()[0]
    nvidia_path = os.path.join(site_packages, "nvidia")
    if os.path.exists(nvidia_path):
        print(f"Nvidia libs found at: {nvidia_path}")
        print("Contents:", os.listdir(nvidia_path))
    else:
        print(f"Nvidia libs NOT found at: {nvidia_path}")
except Exception as e:
    print(f"Error checking nvidia libs: {e}")
