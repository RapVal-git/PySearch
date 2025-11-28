from qdrant_client import QdrantClient
import os

# Conectare la Qdrant
client = QdrantClient(path="qdrant_db")
collection_name = "documente_pdf"

print("=" * 60)
print("📊 INFORMAȚII BAZĂ DE DATE QDRANT")
print("=" * 60)

# 1. Mărimea folderului
folder_path = "qdrant_db"
total_size = 0
file_count = 0

for dirpath, dirnames, filenames in os.walk(folder_path):
    for filename in filenames:
        filepath = os.path.join(dirpath, filename)
        total_size += os.path.getsize(filepath)
        file_count += 1

print(f"\n📁 Mărime folder: {total_size / (1024*1024):.2f} MB")
print(f"📄 Număr fișiere: {file_count}")

# 2. Informații despre colecție
try:
    collections = client.get_collections().collections
    print(f"\n📚 Număr colecții: {len(collections)}")
    
    for collection in collections:
        print(f"\n{'='*60}")
        print(f"Colecție: {collection.name}")
        
        # Obține detalii despre colecție
        info = client.get_collection(collection.name)
        
        print(f"  • Vectori: {info.points_count:,}")
        print(f"  • Dimensiune vector: {info.config.params.vectors.size}")
        print(f"  • Distanță: {info.config.params.vectors.distance}")
        print(f"  • Status: {info.status}")
        
        # Calculează mărimea aproximativă
        # Fiecare vector float32 = 4 bytes
        vector_size_bytes = info.points_count * info.config.params.vectors.size * 4
        vector_size_mb = vector_size_bytes / (1024 * 1024)
        
        print(f"  • Mărime estimată vectori: {vector_size_mb:.2f} MB")
        
        # Obține un exemplu de payload pentru a vedea ce date sunt stocate
        sample = client.scroll(
            collection_name=collection.name,
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        
        if sample[0]:
            print(f"\n  📝 Exemplu payload:")
            payload = sample[0][0].payload
            for key, value in payload.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"    - {key}: {value[:100]}... ({len(value)} caractere)")
                else:
                    print(f"    - {key}: {value}")
        
except Exception as e:
    print(f"\n❌ Eroare la citirea colecției: {e}")

print(f"\n{'='*60}")
