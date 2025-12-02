import os
import time
import uuid
import hashlib
import json
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.http import models
from procesare_text import iterare_chunkuri_document
import config

def calculeaza_hash_fisier(cale_fisier):
    """Calculeaza hash-ul unui fisier pentru a detecta modificari"""
    hash_md5 = hashlib.md5()
    with open(cale_fisier, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def indexare_incrementala(cale_folder):
    # Configuration (din config.py)
    collection_name = config.COLLECTION_NAME
    qdrant_path = config.QDRANT_PATH
    batch_size = config.BATCH_SIZE
    fisier_tracking = config.INDEXED_FILES_JSON

    if not os.path.isdir(cale_folder):
        print(f"Eroare: Folderul '{cale_folder}' nu exista.")
        return

    # Incarca lista de fisiere deja indexate
    fisiere_indexate = {}
    if os.path.exists(fisier_tracking):
        with open(fisier_tracking, "r", encoding="utf-8") as f:
            fisiere_indexate = json.load(f)
    
    # Initialize Qdrant Client
    try:
        client = QdrantClient(path=qdrant_path, timeout=config.QDRANT_TIMEOUT)
        print(f"Conectat la Qdrant Local: {os.path.abspath(qdrant_path)}")
    except Exception as e:
        print(f"Eroare la initializarea Qdrant Local: {e}")
        return

    # Initialize Model
    print("Incarcare model SentenceTransformer...")
    model = SentenceTransformer(config.EMBEDDING_MODEL)

    # Ensure Collection Exists
    collections = client.get_collections()
    if not any(c.name == collection_name for c in collections.collections):
        print(f"Creare colectie '{collection_name}'...")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(size=config.VECTOR_SIZE, distance=models.Distance.COSINE),
        )
        
        # Creăm index pentru căutare lexicală (Full-Text Search)
        print("Creare index lexical pentru 'text_chunk'...")
        client.create_payload_index(
            collection_name=collection_name,
            field_name="text_chunk",
            field_schema=models.TextIndexParams(
                type="text",
                tokenizer=models.TokenizerType.WORD,
                min_token_len=2,
                max_token_len=20,
                lowercase=True
            )
        )

    # Gaseste toate documentele suportate
    print(f"Scanare folder: {cale_folder}...")
    document_paths = []
    
    for root, dirs, files in os.walk(cale_folder):
        for file in files:
            if file.lower().endswith(config.ALL_SUPPORTED_EXTENSIONS):
                document_paths.append(os.path.join(root, file))
    
    # Numără fișiere pe tip
    pdf_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['pdf'])))
    docx_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['docx'])))
    excel_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['excel'])))
    video_count = sum(1 for p in document_paths if p.lower().endswith(tuple(config.SUPPORTED_EXTENSIONS['video'] + config.SUPPORTED_EXTENSIONS['audio'])))
    
    print(f"Gasite {len(document_paths)} fisiere: {pdf_count} PDF, {docx_count} DOCX, {excel_count} EXCEL, {video_count} VIDEO")
    
    # Filtreaza doar fisierele noi sau modificate
    fisiere_de_procesat = []
    for cale_document in document_paths:
        hash_curent = calculeaza_hash_fisier(cale_document)
        
        # Determină tipul fișierului
        ext = cale_document.lower()
        if ext.endswith('.pdf'):
            tip_fisier = "PDF"
        elif ext.endswith('.docx'):
            tip_fisier = "DOCX"
        elif ext.endswith(('.xlsx', '.xls')):
            tip_fisier = "EXCEL"
        else:
            tip_fisier = "VIDEO"
        
        # Verifica daca fisierul e nou sau modificat
        if cale_document not in fisiere_indexate or fisiere_indexate[cale_document] != hash_curent:
            fisiere_de_procesat.append(cale_document)
            print(f"  [NOU/MODIFICAT] {tip_fisier:5s} {os.path.basename(cale_document)}")
        else:
            print(f"  [DEJA INDEXAT] {tip_fisier:5s} {os.path.basename(cale_document)}")
    
    if not fisiere_de_procesat:
        print("\nNu sunt fisiere noi de indexat!")
        return
    
    print(f"\nGasite {len(fisiere_de_procesat)} fisiere noi/modificate din {len(document_paths)} total.")

    # Proceseaza doar fisierele noi
    start_total = time.time()
    points = []
    total_vectors = 0

    for i, cale_document in enumerate(fisiere_de_procesat):
        # Determină tipul fișierului
        ext = cale_document.lower()
        if ext.endswith('.pdf'):
            tip_fisier = "PDF"
        elif ext.endswith('.docx'):
            tip_fisier = "DOCX"
        elif ext.endswith(('.xlsx', '.xls')):
            tip_fisier = "EXCEL"
        else:
            tip_fisier = "VIDEO"
        
        print(f"\n[{i+1}/{len(fisiere_de_procesat)}] Procesare {tip_fisier}: {os.path.basename(cale_document)}")
        
        try:
            # Folosește funcția universală care suportă toate tipurile
            for item in iterare_chunkuri_document(cale_document):
                text = item.get('text_chunk', "")
                if not text:
                    continue

                current_count = total_vectors + len(points) + 1
                print(f"\r   -> Procesat chunk {current_count}...", end="", flush=True)
                vector = model.encode(text).tolist()
                
                payload = item.get('metadata', {})
                payload['text_chunk'] = text
                
                point_id = str(uuid.uuid4())
                points.append(models.PointStruct(id=point_id, vector=vector, payload=payload))

                if len(points) >= batch_size:
                    client.upsert(collection_name=collection_name, points=points)
                    total_vectors += len(points)
                    print(f"\n   -> Urcat batch de {len(points)} vectori (Total: {total_vectors})")
                    points = []
            
            # Marcheaza fisierul ca indexat
            hash_curent = calculeaza_hash_fisier(cale_document)
            fisiere_indexate[cale_document] = hash_curent
            
            # Salveaza progresul
            with open(fisier_tracking, "w", encoding="utf-8") as f:
                json.dump(fisiere_indexate, f, ensure_ascii=False, indent=2)
            
            print(f"\n   Fișier indexat cu succes! Hash salvat: {hash_curent[:8]}...")
                    
        except Exception as e:
            print(f"\n Eroare la procesarea fisierului {cale_document}: {e}")
            print(f"   Hash-ul NU a fost salvat - fișierul va fi re-procesat la următoarea indexare.")

    # Upload remaining points
    if points:
        client.upsert(collection_name=collection_name, points=points)
        total_vectors += len(points)

    durata = time.time() - start_total
    print(f"\n\nIndexare incrementala finalizata in {durata:.2f} secunde.")
    print(f"Total vectori noi indexati: {total_vectors}")

if __name__ == "__main__":
    # Folosește folder-ul din config.py (poate fi suprascris cu variabilă de mediu)
    folder_tinta = config.DEFAULT_INDEXING_FOLDER
    
    print(f"Folder tinta: {folder_tinta}")
    
    # Permite override manual
    user_input = input("Apasati Enter pentru a continua sau introduceti alta cale: ").strip()
    if user_input:
        folder_tinta = user_input

    indexare_incrementala(folder_tinta)
