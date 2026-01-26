from docx import Document
import os
import config


def extrage_text_docx(cale_docx, open_output=False):
    """
    Extrage text din DOCX direct în memorie, fără a salva fișiere TXT intermediare.
    Simulează "pagini" la fiecare 10 paragrafe pentru compatibilitate cu PDF-urile.
    
    Returns:
        Generator care yield-ează tuple (numar_pagina, text_pagina)
    """
    if not os.path.isfile(cale_docx):
        print(f"Eroare: Fisierul {cale_docx} nu exista.")
        return None

    try:
        doc = Document(cale_docx)
        # print(f"Procesare DOCX: {os.path.basename(cale_docx)}")  # Comentat pentru a reduce output-ul
        
        # Extragem toate paragrafele
        paragrafe = [p.text for p in doc.paragraphs if p.text.strip()]
        total_paragrafe = len(paragrafe)
        # print(f"Total paragrafe: {total_paragrafe}")
        
        # Simulăm "pagini" la fiecare N paragrafe (din config.py)
        paragrafe_per_pagina = config.DOCX_PARAGRAPHS_PER_PAGE
        numar_pagina = 1
        text_pagina_curenta = []
        
        for idx, paragraf in enumerate(paragrafe):
            text_pagina_curenta.append(paragraf)
            text_pagina_curenta.append("\n\n")
            
            # La fiecare 10 paragrafe sau la final, yield-ăm pagina
            if (idx + 1) % paragrafe_per_pagina == 0 or idx == total_paragrafe - 1:
                yield (numar_pagina, "".join(text_pagina_curenta))
                numar_pagina += 1
                text_pagina_curenta = []
        
        # Procesăm și tabelele dacă există
        if doc.tables:
            # print(f"Găsite {len(doc.tables)} tabele. Extragere text din tabele...")
            for idx_tabel, tabel in enumerate(doc.tables):
                text_tabel = [f"[Tabel {idx_tabel + 1}]\n"]
                
                for row in tabel.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells)
                    if row_text.strip():
                        text_tabel.append(row_text)
                        text_tabel.append("\n")
                
                text_tabel.append("\n\n")
                yield (numar_pagina, "".join(text_tabel))
                numar_pagina += 1
                    
    except Exception as e:
        print(f"Eroare la procesarea DOCX-ului: {e}")
        return None


if __name__ == "__main__":
    # Test cu un fișier DOCX
    cale_test = r"test.docx"
    if os.path.exists(cale_test):
        for num_pag, text in extrage_text_docx(cale_test):
            print(f"Pagina {num_pag}: {len(text)} caractere")
    else:
        print(f"Pentru testare, creează un fișier {cale_test}")
