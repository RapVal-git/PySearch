import requests
import json

# Testează API-ul pentru a vedea duplicatele
url = "http://localhost:8000/search"
query = "lactic acid bacteria"

response = requests.post(url, json={"query": query, "limit": 20})

if response.status_code == 200:
    results = response.json()
    print(f"Total rezultate: {len(results)}")
    
    # Verifică duplicatele
    seen = {}
    duplicates = []
    
    for idx, result in enumerate(results, 1):
        key = (result['source'], result['page'], result['text'][:100])
        
        if key in seen:
            duplicates.append({
                'original_index': seen[key],
                'duplicate_index': idx,
                'source': result['source'],
                'page': result['page'],
                'score': result['score']
            })
        else:
            seen[key] = idx
    
    if duplicates:
        print(f"\n❌ Găsite {len(duplicates)} duplicate!")
        for dup in duplicates[:5]:
            print(f"  - Rezultatul #{dup['duplicate_index']} este duplicat al #{dup['original_index']}")
            print(f"    Sursă: {dup['source']}, Pagina: {dup['page']}, Scor: {dup['score']:.4f}")
    else:
        print("\n✅ Nu s-au găsit duplicate")
        
    # Arată primele 5 rezultate
    print("\n=== Primele 5 rezultate ===")
    for idx, result in enumerate(results[:5], 1):
        print(f"\n#{idx}")
        print(f"Scor: {result['score']:.4f}")
        print(f"Sursă: {result['source']}")
        print(f"Pagină: {result['page']}")
        print(f"Text: {result['text'][:150]}...")
else:
    print(f"Eroare: {response.status_code}")
    print(response.text)
