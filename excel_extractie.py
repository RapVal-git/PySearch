import openpyxl
import os


def extrage_text_excel(cale_excel):
    """
    Extrage text din fișiere Excel (.xlsx, .xls) direct în memorie.
    
    Args:
        cale_excel: Calea către fișierul Excel
        
    Yields:
        Tuple (numar_sheet, text_sheet)
        Simulăm "pagini" ca sheet-uri Excel
    """
    if not os.path.isfile(cale_excel):
        print(f"Eroare: Fisierul {cale_excel} nu exista.")
        return

    try:
        # Încarcă workbook-ul
        workbook = openpyxl.load_workbook(cale_excel, data_only=True)
        
        for sheet_index, sheet_name in enumerate(workbook.sheetnames):
            sheet = workbook[sheet_name]
            
            # Extrage tot textul din sheet
            text_lines = []
            
            # Iterează prin toate rândurile și coloanele
            for row in sheet.iter_rows(values_only=True):
                # Filtrează celulele None și convertește la string
                row_text = ' | '.join(str(cell) for cell in row if cell is not None)
                if row_text.strip():
                    text_lines.append(row_text)
            
            # Combină toate liniile
            text_sheet = '\n'.join(text_lines)
            
            if text_sheet.strip():
                yield (sheet_index + 1, text_sheet)
        
        workbook.close()
                
    except Exception as e:
        print(f"Eroare la procesarea Excel-ului: {e}")
        return


if __name__ == "__main__":
    # Exemplu de utilizare
    cale_server_excel = r"test.xlsx"
    if os.path.exists(cale_server_excel):
        for num_sheet, text in extrage_text_excel(cale_server_excel):
            print(f"Sheet {num_sheet}: {len(text)} caractere")
            print(f"Preview: {text[:200]}...")
    else:
        print(f"Fișier de test nu există: {cale_server_excel}")
