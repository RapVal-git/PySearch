import json
import os
from sentence_transformers import SentenceTransformer, util
import torch
import time


def motor_cautare_simplu():
    fisier_db = "baza_date_vectoriala.json"
    nume_model = "paraphrase-MiniLM-L6-v2"

    if not os.path.isfile(fisier_db):
        print(f"Eroare: fisierul de baza de date '{fisier_db}' nu exista.")
        return

    model = SentenceTransformer(nume_model)
    with open(fisier_db, "r", encoding="utf-8") as f:
        baze_date = json.load(f)

    print("Baza de date incarcata.")
    embeddings_baza = [item.get('embedding', []) for item in baze_date]

    # convert stored embeddings (lists) into torch tensors
    vector_dim = next((len(e) for e in embeddings_baza if e), None)
    if vector_dim is None:
        print("Eroare: niciun embedding valid gasit in baza de date.")
        return

    embeddings_baza_tensors = [
        torch.tensor(e, dtype=torch.float32) if e else torch.zeros(vector_dim, dtype=torch.float32)
        for e in embeddings_baza
    ]

    while True:
        intrebare = input("Introduceti intrebarea (sau 'exit' pentru a iesi): ")
        if intrebare.lower() == 'exit':
            break
        if len(intrebare) < 3:
            print("Intrebarea este prea scurta. Incercati din nou.")
            continue

        # request a tensor result so semantic_search uses torch tensors
        query_embedding = model.encode(intrebare, convert_to_tensor=True)

        # semantic_search expects query_embeddings as a list
        top_results = util.semantic_search([query_embedding], embeddings_baza_tensors, top_k=3)[0]

        print(f"Top 3 rezultate pentru intrebarea: '{intrebare}'")
        for hit in top_results:
            id_segment = hit['corpus_id']
            score = hit['score']
            segment_gasit = baze_date[id_segment]
            print(f"\nScor: {score:.4f}")
            print(f"Text Chunk: {segment_gasit.get('text_chunk', '')[:200]}")
            metadata = segment_gasit.get('metadata', {})
            print(f"Metadata: {metadata.get('numar_pagina')}, Sursa: {metadata.get('sursa_fisier')}")


if __name__ == "__main__":
    motor_cautare_simplu()
