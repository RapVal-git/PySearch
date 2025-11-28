import os
from qdrant_client import QdrantClient

# Conectare la Qdrant
client = QdrantClient(path="qdrant_db")
collection_name = "documente_pdf"

try:
    # Obține informații despre colecție
    collection_info = client.get_collection(collection_name)
    print(f"✅ Colecția '{collection_name}' există")
    print(f"📊 Număr total de vectori: {collection_info.points_count}")
    
    # Obține câteva exemple pentru a verifica duplicatele
    print("\n🔍 Verificare duplicate...")
    
    # Scroll prin primele 50 de puncte
    result = client.scroll(
        collection_name=collection_name,
        limit=50,
        with_payload=True,
        with_vectors=False
    )
    
    points = result[0]
    
    # Verifică duplicate bazate pe text + pagină + sursă
    seen = {}
    duplicates = []
    
    for point in points:
        text = point.payload.get('text_chunk', '')[:200]  # Primele 200 caractere
        page = point.payload.get('pagina', 0)
        source = point.payload.get('sursa_fisier', '')
        
        key = (text, page, source)
        
        if key in seen:
            duplicates.append({
                'id1': seen[key],
                'id2': point.id,
                'page': page,
                'source': os.path.basename(source) if source else 'Unknown'
            })
        else:
            seen[key] = point.id
    
    if duplicates:
        print(f"❌ Găsite {len(duplicates)} duplicate în primele 50 de puncte!")
        for i, dup in enumerate(duplicates[:5], 1):
            print(f"  {i}. Pagina {dup['page']} din {dup['source']}")
    else:
        print(f"✅ Nu s-au găsit duplicate în primele 50 de puncte")
        
except Exception as e:
    print(f"❌ Eroare: {e}")
    import traceback
    traceback.print_exc()
