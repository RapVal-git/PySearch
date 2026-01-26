from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import time

def cautare_qdrant():
    # Configuration
    collection_name = "documente_pdf"
    # Qdrant Local Mode: Must match the path used in generation
    qdrant_path = "qdrant_db"
    model_name = "paraphrase-MiniLM-L6-v2"

    # Initialize Qdrant Client (Local Mode)
    try:
        client = QdrantClient(path=qdrant_path)
    except Exception as e:
        print(f"Eroare la conectarea cu Qdrant Local: {e}")
        return

    # Initialize Model
    print("Incarcare model...")
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

    print(f"Motor de cautare Qdrant activ. Colectie: {collection_name}")

    while True:
        intrebare = input("\nIntroduceti intrebarea (sau 'exit' pentru a iesi): ")
        if intrebare.lower() == 'exit':
            break
        if len(intrebare) < 3:
            print("Intrebarea este prea scurta.")
            continue

        start_t = time.time()
        
        # Embed Query
        query_vector = model.encode(intrebare).tolist()

        # Search in Qdrant
        try:
            # In qdrant-client 1.16.0, use query_points instead of search
            from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
            
            results = client.query_points(
                collection_name=collection_name,
                query=query_vector,
                limit=10  # Changed from 3 to 10 results
            ).points
        except Exception as e:
            print(f"Eroare la cautare: {e}")
            continue

        durata = time.time() - start_t
        print(f"Cautare finalizata in {durata:.3f} secunde.")
        print(f"Top 10 rezultate pentru: '{intrebare}'")

        for hit in results:
            score = hit.score
            payload = hit.payload
            text = payload.get('text_chunk', 'N/A')
            sursa = payload.get('sursa_fisier', 'N/A')
            pagina = payload.get('pagina', 'N/A')

            print(f"\nScor: {score:.4f}")
            print(f"Text: {text[:200]}...")
            print(f"Sursa: {sursa} (Pagina {pagina})")

if __name__ == "__main__":
    cautare_qdrant()
