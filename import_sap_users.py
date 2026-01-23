import json
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd

USERS_DB_FILE = "users_db.json"
DEFAULT_ROLE = "user"
DEFAULT_GROUPS = ["public"]

EMAIL_COLUMNS = ["e-mail", "email", "e_mail"]
FIRST_NAME_COLUMNS = ["first name", "firstname", "prenume"]
LAST_NAME_COLUMNS = ["last name", "lastname", "surname", "nume"]


def _normalize_column(name: str) -> str:
    return "".join(ch for ch in name.strip().lower() if ch.isalnum())


def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    normalized = {_normalize_column(c): c for c in df.columns}
    for candidate in candidates:
        key = _normalize_column(candidate)
        if key in normalized:
            return normalized[key]
    return None


def _load_existing_users() -> dict:
    if not os.path.exists(USERS_DB_FILE):
        return {}
    try:
        with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        print(f"Error loading {USERS_DB_FILE}: {exc}")
        return {}


def _save_users(users: dict) -> None:
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=True)


def import_sap_users(csv_file: str) -> None:
    print(f"Reading SAP CSV: {csv_file}...")

    try:
        df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
        df.columns = [c.strip() for c in df.columns]
    except Exception as exc:
        print(f"Error reading CSV: {exc}")
        return

    email_col = _find_column(df, EMAIL_COLUMNS)
    first_name_col = _find_column(df, FIRST_NAME_COLUMNS)
    last_name_col = _find_column(df, LAST_NAME_COLUMNS)

    if not email_col:
        print("Missing email column. Expected one of: E-Mail, Email, E-mail")
        return

    users = _load_existing_users()
    now = datetime.utcnow().isoformat() + "Z"
    created = 0
    updated = 0

    for _, row in df.iterrows():
        email = str(row.get(email_col, "")).strip().lower()
        if not email:
            continue

        first_name = str(row.get(first_name_col, "")).strip() if first_name_col else ""
        last_name = str(row.get(last_name_col, "")).strip() if last_name_col else ""
        full_name = " ".join(part for part in [first_name, last_name] if part)

        existing = users.get(email, {})
        password_hash = existing.get("password_hash", "")
        must_set_password = existing.get("must_set_password")
        if must_set_password is None:
            must_set_password = False if password_hash else True

        groups = existing.get("groups", DEFAULT_GROUPS)
        if isinstance(groups, str):
            groups = [groups]
        if "public" not in groups:
            groups = groups + ["public"]

        metadata = existing.get("metadata", {})
        metadata.update({
            "source": "sap_import",
            "last_import": now,
            "sap_row_index": int(row.get("#", "0") or 0)
        })

        users[email] = {
            "password_hash": password_hash,
            "must_set_password": must_set_password if password_hash else True,
            "role": existing.get("role", DEFAULT_ROLE),
            "groups": groups,
            "name": full_name or existing.get("name", email),
            "disabled": existing.get("disabled", False),
            "metadata": metadata,
        }

        if existing:
            updated += 1
        else:
            created += 1

    _save_users(users)
    print("=" * 60)
    print(f"Import complete. Created: {created}, Updated: {updated}")
    print(f"Users saved to: {USERS_DB_FILE}")
    print("Note: New users must set password on first login.")
    print("=" * 60)


if __name__ == "__main__":
    import_sap_users("sap_export.csv")
