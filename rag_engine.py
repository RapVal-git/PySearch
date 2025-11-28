import os
from openai import OpenAI
from typing import List, Dict
import config

class RAGEngine:
    def __init__(self, provider="local", api_key=None, model_name=None):
        """
        Inițializează motorul RAG.
        
        Args:
            provider: "local" (Ollama) sau "openai"
            api_key: Cheia API (pentru OpenAI)
            model_name: Numele modelului (ex: "gpt-3.5-turbo" sau "llama3")
        """
        self.provider = provider
        
        if provider == "openai":
            self.client = OpenAI(api_key=api_key)
            self.model = model_name or "gpt-3.5-turbo"
        else:
            # Configurare pentru Ollama Local (din config.py)
            self.client = OpenAI(
                base_url=config.OLLAMA_BASE_URL,
                api_key='ollama',  # required, but unused
            )
            self.model = model_name or config.OLLAMA_MODEL

    def genereaza_raspuns(self, intrebare: str, context_chunks: List[Dict]) -> str:
        """
        Generează un răspuns bazat pe contextul oferit.
        """
        
        # 1. Construiește contextul din chunk-urile găsite
        context_text = ""
        for i, chunk in enumerate(context_chunks):
            sursa = os.path.basename(chunk.get('sursa_fisier', 'Necunoscut'))
            text = chunk.get('text_chunk', '').strip()
            context_text += f"\n--- SURSA {i+1} ({sursa}) ---\n{text}\n"

        # 2. Construiește prompt-ul sistemului
        system_prompt = """Ești un asistent AI util și precis pentru o companie. 
Răspunde la întrebarea utilizatorului DOAR pe baza informațiilor din contextul furnizat mai jos.
Dacă informația nu există în context, spune clar "Nu am găsit această informație în documentele disponibile."
Nu inventa informații. Citează sursa (numele fișierului) când este posibil."""

        # 3. Trimite la LLM
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context:\n{context_text}\n\nÎntrebare: {intrebare}"}
                ],
                temperature=0.3, # Mai creativ = 0.7, Mai precis = 0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Eroare la generarea răspunsului: {e}"

# Exemplu de utilizare
if __name__ == "__main__":
    # Test simplu (presupune că Ollama rulează local)
    try:
        rag = RAGEngine(provider="local", model_name="llama3")
        
        mock_context = [
            {"sursa_fisier": "Manual_HR.pdf", "text_chunk": "Zilele de concediu se aprobă de managerul direct cu minim 5 zile înainte."},
            {"sursa_fisier": "Proceduri.docx", "text_chunk": "Pentru concediu medical, adeverința se aduce în 24 de ore."}
        ]
        
        print("Generare răspuns test...")
        raspuns = rag.genereaza_raspuns("Cum îmi iau concediu?", mock_context)
        print("\nRăspuns:\n", raspuns)
    except Exception as e:
        print(f"Nu s-a putut testa local: {e}")
