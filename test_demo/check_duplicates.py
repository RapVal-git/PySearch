from qdrant_client import QdrantClient

# Conectare la Qdrant
client = QdrantClient(path="qdrant_db")
collection_name = "documente_pdf"

# Obține informații despre colecție
collection_info = client.get_collection(collection_name)
print(f"Număr total de vectori în colecție: {collection_info.points_count}")
print(f"Vectori count: {collection_info.vectors_count}")

# Obține câteva exemple de puncte pentru a verifica duplicatele
points = client.scroll(
    collection_name=collection_name,
    limit=20,
    with_payload=True,
    with_vectors=False
)

print("\n=== Primele 20 puncte ===")
for idx, point in enumerate(points[0], 1):
    print(f"\n#{idx}")
    print(f"ID: {point.id}")
    print(f"Sursă: {point.payload.get('sursa_fisier', 'N/A')}")
    print(f"Pagină: {point.payload.get('pagina', 'N/A')}")
    print(f"Text preview: {point.payload.get('text_chunk', '')[:100]}...")
