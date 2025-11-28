from qdrant_client import QdrantClient

# Conectare la Qdrant
qdrant_path = "qdrant_db"
collection_name = "documente_pdf"

print("⚠️  ATENȚIE: Acest script va șterge complet colecția Qdrant!")
print(f"Colecție: {collection_name}")
print(f"Path: {qdrant_path}")

response = input("\nEști sigur că vrei să continui? (da/nu): ")

if response.lower() == "da":
    try:
        client = QdrantClient(path=qdrant_path)
        
        # Verifică dacă colecția există
        collections = client.get_collections().collections
        collection_exists = any(c.name == collection_name for c in collections)
        
        if collection_exists:
            # Obține info înainte de ștergere
            info = client.get_collection(collection_name)
            print(f"\n📊 Colecția conține {info.points_count} vectori")
            
            # Șterge colecția
            client.delete_collection(collection_name)
            print(f"✅ Colecția '{collection_name}' a fost ștearsă cu succes!")
            print("\n📝 Următorii pași:")
            print("1. Rulează din nou indexare_folder_qdrant.py pentru a re-indexa documentele")
            print("2. Asigură-te că rulezi scriptul o singură dată!")
        else:
            print(f"❌ Colecția '{collection_name}' nu există!")
            
    except Exception as e:
        print(f"❌ Eroare: {e}")
else:
    print("❌ Operațiune anulată")
