import hashlib
import getpass
import sys

def create_user_entry():
    print("\n╔══════════════════════════════════════════════╗")
    print("║      GENERATOR UTILIZATORI NOI               ║")
    print("╚══════════════════════════════════════════════╝")
    
    # 1. Colectare date
    while True:
        username = input("\n👤 Username (ex: ion.popescu): ").strip()
        if username: break
        print("❌ Username-ul nu poate fi gol!")

    while True:
        password = getpass.getpass("🔑 Parola: ").strip()
        if password: break
        print("❌ Parola nu poate fi goală!")

    print("\nRoluri disponibile: admin, manager, hr, finance, user")
    role = input("🛡️  Rol: ").strip() or "user"

    name = input("📝 Nume Complet (ex: Ion Popescu): ").strip()

    # 2. Generare Hash
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # 3. Afișare Rezultat
    print("\n✅ GATA! Copiază codul de mai jos în 'auth_config.py' sau 'auth_config_advanced.py':")
    print("\n" + "="*50)
    
    print(f'    "{username}": {{')
    print(f'        "password_hash": "{password_hash}",')
    print(f'        "role": "{role}",')
    print(f'        "name": "{name}"')
    print('    },')
    
    print("="*50 + "\n")

if __name__ == "__main__":
    try:
        while True:
            create_user_entry()
            if input("Adaugi alt utilizator? (d/n): ").lower() != 'd':
                break
    except KeyboardInterrupt:
        print("\n\nOperațiune anulată.")
