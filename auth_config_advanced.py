"""
Versiune Avansată: Control Acces cu Pattern Matching
Funcționează cu ORICE structură de foldere, fără reorganizare
"""

import hashlib
import re
from typing import List, Dict, Optional


# ============================================================================
# CONFIGURARE UTILIZATORI
# ============================================================================

import json
import os

# ============================================================================
# CONFIGURARE UTILIZATORI (Load from JSON)
# ============================================================================

USERS_DB_FILE = "users_db.json"

def load_users():
    """Încarcă utilizatorii din fișierul JSON sau folosește default"""
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Eroare la încărcarea {USERS_DB_FILE}: {e}")
    
    # Fallback users (dacă nu există fișierul)
    return {
        "admin": {
            "password_hash": hashlib.sha256("admin123".encode()).hexdigest(),
            "role": "admin",
            "name": "Administrator"
        }
    }

USERS = load_users()


# ============================================================================
# PERMISIUNI BAZATE PE PATTERNS (Flexibil!)
# ============================================================================

# Patterns pentru foldere/fișiere SENSIBILE (blocate implicit)
SENSITIVE_PATTERNS = {
    "hr_only": [
        r"\\HR\\",              # Orice folder numit HR
        r"\\Salarii\\",         # Orice folder numit Salarii
        r"\\Evaluari\\",        # Orice folder numit Evaluari
        r"_salarial_",          # Fișiere cu "_salarial_" în nume
        r"_angajat_",           # Fișiere cu "_angajat_" în nume
    ],
    "finance_only": [
        r"\\Financiar\\",       # Orice folder numit Financiar
        r"\\Facturi\\",         # Orice folder numit Facturi
        r"\\Bugete\\",          # Orice folder numit Bugete
        r"_financiar_",         # Fișiere cu "_financiar_" în nume
        r"_buget_",             # Fișiere cu "_buget_" în nume
    ],
    "admin_only": [
        r"\\Confidential\\",    # Folder Confidential
        r"\\Legal\\",           # Folder Legal
        r"\\Audit\\",           # Folder Audit
        r"_confidential_",      # Fișiere confidențiale
    ]
}

# Patterns pentru foldere PUBLIC (accesibile tuturor)
PUBLIC_PATTERNS = [
    r"\\Public\\",              # Orice folder numit Public
    r"\\Shared\\",              # Orice folder numit Shared
    r"\\Common\\",              # Orice folder numit Common
    r"_public_",                # Fișiere cu "_public_" în nume
]

# Patterns pentru fiecare rol (ce AU VOIE să vadă)
ROLE_PATTERNS = {
    "admin": [".*"],  # Vede TOT (wildcard)
    
    "manager": [
        r"\\Contracte\\",
        r"\\Proiecte\\",
        r"\\Rapoarte\\",
        r"\\Management\\",
        r"_contract_",
        r"_proiect_",
    ],
    
    "hr": [
        r"\\HR\\",
        r"\\Salarii\\",
        r"\\Evaluari\\",
        r"\\Recrutare\\",
    ],
    
    "finance": [
        r"\\Financiar\\",
        r"\\Facturi\\",
        r"\\Bugete\\",
        r"\\Contabilitate\\",
    ],
    
    "user": []  # Doar Public
}


# ============================================================================
# FUNCȚII DE VERIFICARE ACCES (Pattern Matching)
# ============================================================================

def matches_any_pattern(file_path: str, patterns: List[str]) -> bool:
    """Verifică dacă path-ul match-uiește vreun pattern"""
    for pattern in patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def is_public_path(file_path: str) -> bool:
    """Verifică dacă path-ul este public"""
    return matches_any_pattern(file_path, PUBLIC_PATTERNS)


def is_sensitive_for_role(file_path: str, role: str) -> bool:
    """
    Verifică dacă path-ul este sensibil și utilizatorul NU are acces
    """
    # Admin vede tot
    if role == "admin":
        return False
    
    # Verifică fiecare categorie de sensibilitate
    for category, patterns in SENSITIVE_PATTERNS.items():
        if matches_any_pattern(file_path, patterns):
            # E sensibil - verifică dacă rolul are acces
            if category == "hr_only" and role == "hr":
                return False  # HR are acces la HR
            elif category == "finance_only" and role == "finance":
                return False  # Finance are acces la Finance
            elif category == "admin_only":
                return True  # Doar admin
            else:
                return True  # Blocat pentru acest rol
    
    return False  # Nu e sensibil


def user_can_access_path(username: str, file_path: str) -> bool:
    """
    Verifică dacă utilizatorul are acces la un fișier
    Folosește pattern matching - funcționează cu ORICE structură!
    """
    role = get_user_role(username)
    if not role:
        return False
    
    # 1. Admin vede tot
    if role == "admin":
        return True
    
    # 2. Verifică dacă e public (toată lumea vede)
    if is_public_path(file_path):
        return True
    
    # 3. Verifică dacă e sensibil și blocat pentru acest rol
    if is_sensitive_for_role(file_path, role):
        return False
    
    # 4. Verifică dacă match-uiește patterns-urile rolului
    role_patterns = ROLE_PATTERNS.get(role, [])
    if role_patterns and matches_any_pattern(file_path, role_patterns):
        return True
    
    # 5. Default: nu are acces (pentru siguranță)
    return False


# ============================================================================
# FUNCȚII DE AUTENTIFICARE (Identice cu versiunea simplă)
# ============================================================================

def verify_password(username: str, password: str) -> bool:
    """Verifică username și parolă"""
    if username not in USERS:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return USERS[username]["password_hash"] == password_hash


def get_user_role(username: str) -> Optional[str]:
    """Returnează rolul utilizatorului"""
    if username in USERS:
        return USERS[username]["role"]
    return None


def filter_results_by_user(results: List[Dict], username: str) -> List[Dict]:
    """Filtrează rezultatele bazat pe permisiuni"""
    filtered = []
    
    for result in results:
        file_path = result.get("payload", {}).get("sursa_fisier", "")
        
        if user_can_access_path(username, file_path):
            filtered.append(result)
    
    return filtered


def get_allowed_folders(username: str) -> List[str]:
    """Returnează patterns-urile la care utilizatorul are acces"""
    role = get_user_role(username)
    if not role:
        return []
    
    if role == "admin":
        return ["*"]
    
    patterns = ROLE_PATTERNS.get(role, [])
    return patterns + PUBLIC_PATTERNS


# ============================================================================
# FUNCȚII HELPER
# ============================================================================

def add_sensitive_pattern(category: str, pattern: str):
    """Adaugă un pattern sensibil"""
    if category not in SENSITIVE_PATTERNS:
        SENSITIVE_PATTERNS[category] = []
    
    if pattern not in SENSITIVE_PATTERNS[category]:
        SENSITIVE_PATTERNS[category].append(pattern)


def add_role_pattern(role: str, pattern: str):
    """Adaugă un pattern pentru un rol"""
    if role not in ROLE_PATTERNS:
        ROLE_PATTERNS[role] = []
    
    if pattern not in ROLE_PATTERNS[role]:
        ROLE_PATTERNS[role].append(pattern)


# ============================================================================
# EXEMPLE DE UTILIZARE
# ============================================================================

if __name__ == "__main__":
    print("=== Test Pattern Matching ===\n")
    
    test_paths = [
        "\\\\Server\\Archive\\2024\\HR\\salarii.xlsx",
        "\\\\Server\\Archive\\2024\\Financiar\\raport.xlsx",
        "\\\\Server\\Archive\\2024\\Public\\anunt.pdf",
        "\\\\Server\\Archive\\2024\\Contracte\\contract_ABC.pdf",
        "\\\\Server\\Shared\\document_public.pdf",
        "\\\\Server\\Archive\\2024\\Confidential\\legal.pdf",
    ]
    
    users = ["admin", "manager", "hr", "finance", "user1"]
    
    # Tabel rezultate
    print(f"{'Path':<50s} | ", end="")
    for user in users:
        print(f"{user:<8s} | ", end="")
    print()
    print("-" * 100)
    
    for path in test_paths:
        filename = path.split("\\")[-1]
        print(f"{filename:<50s} | ", end="")
        
        for user in users:
            has_access = user_can_access_path(user, path)
            symbol = "✅" if has_access else "❌"
            print(f"{symbol:^8s} | ", end="")
        print()
    
    print("\n=== Patterns pentru fiecare rol ===\n")
    for user in users:
        role = get_user_role(user)
        patterns = get_allowed_folders(user)
        print(f"{user} ({role}):")
        if "*" in patterns:
            print("  - ACCES COMPLET (toate folderele)")
        else:
            for pattern in patterns[:5]:  # Primele 5
                print(f"  - {pattern}")
        print()
