import fitz # PyMuPDF
import os
from pdf_extractie import extrage_text_pdf
from docx_extractie import extrage_text_docx
from video_extractie import extrage_text_video
from excel_extractie import extrage_text_excel

def imparte_text_in_chunkuri(text, marime_chunk=1024, suprapunere=100):
    """Generator care imparte textul in chunkuri de marime specificata,
    cu o suprapunere data. Yield-eaza fiecare chunk in loc sa construiasca
    o lista completa (reduce utilizarea memoriei).
    """
    if not text:
        return
    start = 0
    text_len = len(text)
    last_chunk = None
    while start < text_len:
        end = start + marime_chunk
        # initial slice
        if end < text_len:
            segment = text[start:end]
            # try to avoid chopping in the middle of a word
            last_space = segment.rfind(' ')
            if last_space != -1:
                end = start + last_space + 1
                segment = text[start:end]
        else:
            segment = text[start:end]

        current = segment.strip()
        # skip empty or identical consecutive chunks to avoid repetition
        if current and current != last_chunk:
            # print(f"DEBUG: Yielding chunk len={len(current)}")  # Comentat pentru a reduce output-ul
            yield current
            last_chunk = current

        # Calculate next start position
        next_start = end - suprapunere
        
        # Prevent infinite loop: ensure we advance at least 1 character
        if next_start <= start:
            next_start = start + 1
            
        start = next_start
        
        # print(f"DEBUG: Next start={start}, End was={end}") # Uncomment if needed

def pipeline_impartire_pdf_in_chunkuri(cale_pdf):
    """Generator wrapper: extrage si yield-eaza chunkurile produsului PDF.

    Aceasta functie ofera o interfata compatibila dar stream-uita, astfel
    consumatorii pot itera peste rezultate fara a construi o lista mare in memorie.
    """
    # delegate to the existing generator which handles extraction and parsing
    yield from iterare_chunkuri_pdf(cale_pdf)


def iterare_chunkuri_pdf(cale_pdf):
    """Generator: procesează PDF direct în memorie și yield-ează chunk-uri.
    Nu mai creează fișiere TXT intermediare.
    """
    try:
        # Folosim generatorul din pdf_extractie care returnează (numar_pagina, text_pagina)
        for numer_pagina, text_pagina in extrage_text_pdf(cale_pdf):
            # Împărțim textul paginii în chunk-uri
            for bucata in imparte_text_in_chunkuri(text_pagina):
                yield {
                    'text_chunk': bucata,
                    'metadata': {
                        'sursa_fisier': cale_pdf,
                        'pagina': numer_pagina,
                        'tip_document': 'PDF'
                    }
                }
    except Exception as e:
        print(f"Eroare la procesarea PDF {cale_pdf}: {e}")
        return


def iterare_chunkuri_docx(cale_docx):
    """Generator: procesează DOCX direct în memorie și yield-ează chunk-uri.
    Nu mai creează fișiere TXT intermediare.
    """
    try:
        # Folosim generatorul din docx_extractie care returnează (numar_pagina, text_pagina)
        for numer_pagina, text_pagina in extrage_text_docx(cale_docx):
            # Împărțim textul paginii în chunk-uri
            for bucata in imparte_text_in_chunkuri(text_pagina):
                yield {
                    'text_chunk': bucata,
                    'metadata': {
                        'sursa_fisier': cale_docx,
                        'pagina': numer_pagina,
                        'tip_document': 'DOCX'
                    }
                }
    except Exception as e:
        print(f"Eroare la procesarea DOCX {cale_docx}: {e}")
        return


def iterare_chunkuri_video(cale_video):
    """Generator: procesează VIDEO folosind Whisper și yield-ează chunk-uri.
    """
    chunk_count = 0
    try:
        # Folosim generatorul din video_extractie care returnează (timestamp, text_segment)
        for timestamp, text_segment in extrage_text_video(cale_video):
            # Împărțim textul segmentului în chunk-uri
            for bucata in imparte_text_in_chunkuri(text_segment):
                chunk_count += 1
                yield {
                    'text_chunk': bucata,
                    'metadata': {
                        'sursa_fisier': cale_video,
                        'pagina': timestamp, # Folosim timestamp-ul ca "pagină"
                        'tip_document': 'VIDEO'
                    }
                }
        print(f"   -> Procesare video completă: {chunk_count} chunk-uri generate")
    except Exception as e:
        print(f"Eroare la procesarea VIDEO {cale_video}: {e}")
        # Re-raise pentru a notifica indexarea că procesarea a eșuat
        raise


def iterare_chunkuri_excel(cale_excel):
    """Generator: procesează EXCEL direct în memorie și yield-ează chunk-uri.
    Nu mai creează fișiere TXT intermediare.
    """
    try:
        # Folosim generatorul din excel_extractie care returnează (numar_sheet, text_sheet)
        for numar_sheet, text_sheet in extrage_text_excel(cale_excel):
            # Împărțim textul sheet-ului în chunk-uri
            for bucata in imparte_text_in_chunkuri(text_sheet):
                yield {
                    'text_chunk': bucata,
                    'metadata': {
                        'sursa_fisier': cale_excel,
                        'pagina': numar_sheet,  # Folosim numărul sheet-ului ca "pagină"
                        'tip_document': 'EXCEL'
                    }
                }
    except Exception as e:
        print(f"Eroare la procesarea EXCEL {cale_excel}: {e}")
        return


def iterare_chunkuri_document(cale_fisier):
    """
    Generator universal: detectează tipul documentului (PDF, DOCX, EXCEL sau VIDEO) și 
    apelează funcția corespunzătoare de procesare.
    
    Args:
        cale_fisier: Calea către fișierul document
        
    Yields:
        Dict cu 'text_chunk' și 'metadata' pentru fiecare chunk
    """
    extensie = os.path.splitext(cale_fisier)[1].lower()
    
    if extensie == '.pdf':
        yield from iterare_chunkuri_pdf(cale_fisier)
    elif extensie == '.docx':
        yield from iterare_chunkuri_docx(cale_fisier)
    elif extensie in ['.xlsx', '.xls']:
        yield from iterare_chunkuri_excel(cale_fisier)
    elif extensie in ['.mp4', '.avi', '.mov', '.mkv', '.mp3', '.wav']:
        yield from iterare_chunkuri_video(cale_fisier)
    else:
        print(f"Tip de fișier nesuportat: {extensie}")
        return


if __name__ == "__main__":
    import json
    
    # Test cu PDF
    cale_test_pdf = r"test.pdf"
    if os.path.exists(cale_test_pdf):
        print("=== Test PDF ===")
        chunk_count = 0
        for item in iterare_chunkuri_document(cale_test_pdf):
            chunk_count += 1
            if chunk_count <= 2:
                print(f"Chunk {chunk_count}: {item['metadata']}")
                print(f"Text: {item['text_chunk'][:100]}...")
        print(f"Total chunk-uri PDF: {chunk_count}\n")
    
    # Test cu DOCX
    cale_test_docx = r"test.docx"
    if os.path.exists(cale_test_docx):
        print("=== Test DOCX ===")
        chunk_count = 0
        for item in iterare_chunkuri_document(cale_test_docx):
            chunk_count += 1
            if chunk_count <= 2:
                print(f"Chunk {chunk_count}: {item['metadata']}")
                print(f"Text: {item['text_chunk'][:100]}...")
        print(f"Total chunk-uri DOCX: {chunk_count}")
