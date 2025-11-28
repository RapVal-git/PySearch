import fitz
import os


def extrage_text_pdf(cale_pdf, open_output=False):
    """
    Extrage text din PDF direct în memorie, fără a salva fișiere TXT intermediare.
    
    Returns:
        Generator care yield-ează tuple (numar_pagina, text_pagina)
    """
    if not os.path.isfile(cale_pdf):
        print(f"Eroare: Fisierul {cale_pdf} nu exista.")
        return None

    try:
        with fitz.open(cale_pdf) as doc:
            # print(f"Procesare PDF: {os.path.basename(cale_pdf)}")  # Comentat pentru a reduce output-ul
            # print(f"Total pagini: {doc.page_count}")
            
            for numar_pagina, pagina in enumerate(doc):
                text_pagina = pagina.get_text()
                yield (numar_pagina + 1, text_pagina)
                
    except Exception as e:
        print(f"Eroare la procesarea PDF-ului: {e}")
        return None


if __name__ == "__main__":
    # Exemplu de utilizare
    cale_server_pdf = r"test.pdf"
    if os.path.exists(cale_server_pdf):
        for num_pag, text in extrage_text_pdf(cale_server_pdf):
            print(f"Pagina {num_pag}: {len(text)} caractere")
    else:
        print(f"Fișier de test nu există: {cale_server_pdf}")
