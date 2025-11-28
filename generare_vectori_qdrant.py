from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
import json
import os
import time
import uuid

def genereaza_vectori_qdrant():
    # Configuration
    fisier_intrare = "date_vectori.json"
    collection_name = "documente_pdf"
    # Qdrant Local Mode: Save DB to a folder named "qdrant_db"
    qdrant_path = "qdrant_db" 
    batch_size = 100

    # Check input file
    if not os.path.isfile(fisier_intrare):
        print(f"Eroare: Fisierul de intrare '{fisier_intrare}' nu a fost gasit.")
        return

    # Initialize Qdrant Client (Local Mode)
    try:
        client = QdrantClient(path=qdrant_path)
        print(f"Conectat la Qdrant Local: {os.path.abspath(qdrant_path)}")
    except Exception as e:
        print(f"Eroare la initializarea Qdrant Local: {e}")
        return

    # Initialize Model
    print("Incarcare model SentenceTransformer...")
    model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

    # Create Collection if not exists
    collections = client.get_collections()
    collection_exists = any(c.name == collection_name for c in collections.collections)
    
    if not collection_exists:
        print(f"Creare colectie '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
    else:
        print(f"Colectia '{collection_name}' exista deja.")

    # Load Data
    print("Citire date din fisier...")
    with open(fisier_intrare, "r", encoding="utf-8") as f:
        lista_documente = json.load(f)

    print(f"Incepe procesarea a {len(lista_documente)} documente...")
    start_time = time.time()

    points = []
    for i, doc in enumerate(lista_documente):
        text = doc.get('text_chunk', "")
        if not text:
            continue

        # Generate Embedding
        vector = model.encode(text).tolist()
        
        # Prepare Payload (Metadata)
        payload = doc.get('metadata', {})
        payload['text_chunk'] = text # Store text in payload for retrieval

        # Create Point
        point_id = str(uuid.uuid4()) # Generate unique ID
        points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

        # Upload Batch
        if len(points) >= batch_size:
            client.upsert(collection_name=collection_name, points=points)
            print(f"Urcat batch de {len(points)} vectori (Total: {i+1})")
            points = []

    # Upload remaining points
    if points:
        client.upsert(collection_name=collection_name, points=points)
        print(f"Urcat ultimul batch de {len(points)} vectori.")

    durata = time.time() - start_time
    print(f"Finalizat in {durata:.2f} secunde.")

if __name__ == "__main__":
    genereaza_vectori_qdrant()
