FROM python:3.10-slim

# Setează working directory
WORKDIR /app

# Instalează dependențe sistem
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

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
