import pandas as pd
import hashlib
import json
import os

# ============================================================================
# CONFIGURARE MAPPING (Legătura SAP -> Aplicație)
# ============================================================================

# Cum transformăm departamentele din SAP în roluri din aplicația noastră
# Format: "Nume Departament SAP": "Rol Aplicație"
DEPARTMENT_MAPPING = {
    "IT Department": "admin",
    "Human Resources": "hr",
    "HR": "hr",
    "Finance Dept": "finance",
    "Accounting": "finance",
    "Sales": "manager",
    "Management": "manager",
    "Logistics": "user",
    "Production": "user"
}

# Rol implicit dacă departamentul nu e în listă
DEFAULT_ROLE = "user"

# Parola implicită pentru toți utilizatorii importați
DEFAULT_PASSWORD = "Start123!"

def generate_password_hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def import_sap_users(excel_file):
    print(f"🔄 Citire fișier SAP: {excel_file}...")
    
    try:
        # Citește Excel-ul
        # Presupunem coloanele: 'Username', 'FullName', 'Department', 'Company'
        df = pd.read_excel(excel_file)
        
        # Normalizează numele coloanelor (opțional, ca să fim siguri)
        df.columns = [c.strip() for c in df.columns]
        
    except Exception as e:
        print(f"❌ Eroare la citirea fișierului: {e}")
        return

    imported_users = {}
    stats = {"admin": 0, "hr": 0, "finance": 0, "manager": 0, "user": 0}

    print("\nProcesare utilizatori...")
    
    for index, row in df.iterrows():
        username = str(row.get('Username', '')).strip().lower()
        full_name = str(row.get('FullName', '')).strip()
        department = str(row.get('Department', '')).strip()
        company = str(row.get('Company', '')).strip()

        if not username or username == 'nan':
            continue

        # 1. Determină Rolul bazat pe Departament
        role = DEFAULT_ROLE
        
        # Căutare exactă sau parțială
        for sap_dept, app_role in DEPARTMENT_MAPPING.items():
            if sap_dept.lower() in department.lower():
                role = app_role
                break
        
        # 2. Creează intrarea utilizatorului
        imported_users[username] = {
            "password_hash": generate_password_hash(DEFAULT_PASSWORD),
            "role": role,
            "name": full_name,
            "metadata": {
                "department": department,
                "company": company,
                "source": "sap_import"
            }
        }
        
        if role in stats:
            stats[role] += 1
        
        print(f"  ✅ Importat: {username:<15} | Dept: {department:<20} -> Rol: {role}")

    # Salvare în fișier JSON
    output_file = "users_db.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(imported_users, f, indent=4, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"🎉 Import finalizat! Utilizatori salvați în '{output_file}'")
    print(f"📊 Statistici:")
    for role, count in stats.items():
        print(f"   - {role}: {count}")
    print(f"{'='*50}")
    print(f"\n⚠️  NOTĂ: Toți utilizatorii au parola inițială: '{DEFAULT_PASSWORD}'")

# Creare fișier Excel dummy pentru testare (dacă nu există)
def create_dummy_sap_export():
    if not os.path.exists("sap_export_test.xlsx"):
        data = {
            "Username": ["ion.popescu", "maria.ionescu", "andrei.vlad", "elena.dumitru", "admin.sap"],
            "FullName": ["Ion Popescu", "Maria Ionescu", "Andrei Vlad", "Elena Dumitru", "SAP Admin"],
            "Department": ["Logistics", "Human Resources", "Finance Dept", "Sales GMBH", "IT Department"],
            "Company": ["Firma A", "Firma A", "Firma B", "Firma A", "HQ"]
        }
        df = pd.DataFrame(data)
        df.to_excel("sap_export_test.xlsx", index=False)
        print("ℹ️  Am creat un fișier de test 'sap_export_test.xlsx'")

if __name__ == "__main__":
    # Creează date de test
    create_dummy_sap_export()
    
    # Rulează importul
    import_sap_users("sap_export_test.xlsx")
