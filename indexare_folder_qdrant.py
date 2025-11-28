import os
import time
import uuid
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from procesare_text import iterare_chunkuri_document
import config

def indexare_folder_qdrant(cale_folder):
    # Configuration (din config.py)
    collection_name = config.COLLECTION_NAME
    qdrant_path = config.QDRANT_PATH
    batch_size = config.BATCH_SIZE

    if not os.path.isdir(cale_folder):
        print(f"Eroare: Folderul '{cale_folder}' nu exista.")
        return

    # Initialize Qdrant Client (Local Mode)
    try:
        client = QdrantClient(path=qdrant_path, timeout=config.QDRANT_TIMEOUT)
        print(f"Conectat la Qdrant Local: {os.path.abspath(qdrant_path)}")
    except Exception as e:
        print(f"Eroare la initializarea Qdrant Local: {e}")
        return

    # Initialize Model
    print("Incarcare model SentenceTransformer...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    # Delete existing collection if it exists (to prevent duplicates)
    collections = client.get_collections()
    if any(c.name == collection_name for c in collections.collections):
        print(f"  Colecția '{collection_name}' există deja. Ștergere...")
        client.delete_collection(collection_name)
        print(f" Colecție ștearsă")
    
    # Create fresh collection
    print(f"Creare colecție nouă '{collection_name}'...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=config.VECTOR_SIZE, distance=models.Distance.COSINE),
    )
    print(f" Colecție creată")

    # Find all supported files
    print(f"Scanare folder: {cale_folder}...")
    document_paths = []
    
    for root, dirs, files in os.walk(cale_folder):
        for file in files:
            if file.lower().endswith(config.ALL_SUPPORTED_EXTENSIONS):
                document_paths.append(os.path.join(root, file))
    
    total_files = len(document_paths)
    
    # Count by type
    pdf_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['pdf'])))
    docx_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['docx'])))
    excel_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['excel'])))
    video_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['video'] + config.SUPPORTED_EXTENSIONS['audio'])))
    
    print(f"Gasite {total_files} fisiere: {pdf_count} PDF, {docx_count} DOCX, {excel_count} EXCEL, {video_count} VIDEO")

    # Process Files
    start_total = time.time()
    points = []
    total_vectors = 0

    for i, cale_document in enumerate(document_paths):
        ext = cale_document.lower()
        if ext.endswith('.pdf'):
            tip_fisier = "PDF"
        elif ext.endswith('.docx'):
            tip_fisier = "DOCX"
        elif ext.endswith(('.xlsx', '.xls')):
            tip_fisier = "EXCEL"
        else:
            tip_fisier = "VIDEO"
            
        print(f"[{i+1}/{total_files}] Procesare {tip_fisier}: {os.path.basename(cale_document)}")
        
        try:
            # Stream chunks from document (PDF or DOCX)
            for item in iterare_chunkuri_document(cale_document):
                text = item.get('text_chunk', "")
                if not text:
                    continue

                # Generate Embedding
                # Generate Embedding
                current_count = total_vectors + len(points) + 1
                print(f"\r   -> Procesat chunk {current_count}...", end="", flush=True)
                vector = model.encode(text).tolist()
                
                # Prepare Payload
                payload = item.get('metadata', {})
                payload['text_chunk'] = text
                
                # Create Point
                point_id = str(uuid.uuid4())
                points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

                # Upload Batch
                if len(points) >= batch_size:
                    client.upsert(collection_name=collection_name, points=points)
                    total_vectors += len(points)
                    print(f"   -> Urcat batch de {len(points)} vectori (Total fisier: {total_vectors})")
                    points = []
                    
        except Exception as e:
            print(f"Eroare la procesarea fisierului {cale_document}: {e}")

    # Upload remaining points
    if points:
        client.upsert(collection_name=collection_name, points=points)
        total_vectors += len(points)

    durata = time.time() - start_total
    print(f"\nIndexare finalizata in {durata:.2f} secunde.")
    print(f"Total vectori indexati: {total_vectors}")

if __name__ == "__main__":
    # Folder implicit din config.py (poate fi suprascris cu variabilă de mediu INDEXING_FOLDER)
    folder_tinta = config.DEFAULT_INDEXING_FOLDER
    
    # Allow user to override via input if they want
    print(f"Folder tinta implicit: {folder_tinta}")
    user_input = input("Apasati Enter pentru a continua sau introduceti alta cale: ").strip()
    if user_input:
        folder_tinta = user_input

    indexare_folder_qdrant(folder_tinta)
