from qdrant_client import QdrantClient
import shutil
import os

qdrant_path = "qdrant_db"

print("🗑️  Ștergere completă bază de date Qdrant")
print(f"Path: {qdrant_path}")

try:
    # Încearcă să ștergi prin client mai întâi
    print("\n1️⃣ Încercare ștergere prin Qdrant client...")
    client = QdrantClient(path=qdrant_path)
    
    # Obține toate colecțiile
    collections = client.get_collections().collections
    print(f"   Găsite {len(collections)} colecții")
    
    for collection in collections:
        print(f"   Ștergere colecție: {collection.name}")
        client.delete_collection(collection.name)
    
    print("   ✅ Colecții șterse prin client")
    
except Exception as e:
    print(f"   ⚠️  Eroare la ștergere prin client: {e}")

# Ștergere fizică a folderului
print("\n2️⃣ Ștergere fizică a folderului...")
if os.path.exists(qdrant_path):
    try:
        shutil.rmtree(qdrant_path)
        print(f"   ✅ Folder '{qdrant_path}' șters complet!")
    except Exception as e:
        print(f"   ❌ Eroare la ștergere folder: {e}")
        print(f"   💡 Închide toate procesele care folosesc Qdrant și șterge manual folderul '{qdrant_path}'")
else:
    print(f"   ℹ️  Folderul '{qdrant_path}' nu există")

print("\n✅ Proces finalizat!")
print("\n📝 Următorii pași:")
print("1. Rulează indexare_folder_qdrant.py pentru a re-indexa documentele")
print("2. Pornește API-ul: python api_cautare.py")
