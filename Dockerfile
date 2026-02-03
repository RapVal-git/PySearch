FROM nvcr.io/nvidia/pytorch:24.10-py3

# Setează working directory
WORKDIR /app
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility
ENV CELERY_BROKER_URL=redis://redis:6379/0
ENV CELERY_RESULT_BACKEND=redis://redis:6379/1
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsm6 \
    libxext6 \
    ca-certificates \
    openssl \
    && rm -rf /var/lib/apt/lists/*

RUN update-ca-certificates

# Copiază requirements
COPY requirements.txt .

# Instalează dependențe Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Instalează dependențe suplimentare pentru producție
RUN pip install --no-cache-dir \
    python-docx \
    openai-whisper \
    moviepy \
    gunicorn \
    prometheus-fastapi-instrumentator

# Copiază codul aplicației
COPY . .

# Creează directoare necesare
RUN mkdir -p /app/qdrant_db /app/logs

# Expune portul
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comandă de pornire (va fi suprascrisă în docker-compose)
CMD ["python", "api_cautare.py"]
