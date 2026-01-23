import hashlib
import json
import os
import re
from typing import Dict, List, Optional

USERS_DB_FILE = "users_db.json"
PUBLIC_GROUP = "public"

# Public roots (all users must have access here)
PUBLIC_FOLDER_ROOTS = [
    r"\\192.168.27.44\ERP-implementare"
]

# Group-specific roots (accessible only to those groups)
GROUP_FOLDER_ROOTS = {
    "it": [r"\\192.168.27.44\it\AI"]
}

# Public patterns (fallback)
PUBLIC_PATTERNS = [
    r"\\Public\\",
    r"\\Shared\\",
    r"\\Common\\",
    r"_public_",
]

ROLE_TO_GROUPS = {
    "admin": ["admin", PUBLIC_GROUP],
    "manager": ["manager", PUBLIC_GROUP],
    "hr": ["hr", PUBLIC_GROUP],
    "finance": ["finance", PUBLIC_GROUP],
    "user": [PUBLIC_GROUP],
}


def _normalize_path(path: str) -> str:
    if not path:
        return ""
    return path.replace("/", "\\").strip().lower()


def _matches_any_pattern(file_path: str, patterns: List[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, file_path, re.IGNORECASE):
            return True
    return False


def _ensure_public_group(groups: List[str]) -> List[str]:
    normalized = [g.strip() for g in groups if g and g.strip()]
    if PUBLIC_GROUP not in normalized:
        normalized.append(PUBLIC_GROUP)
    return normalized


def load_users() -> Dict[str, Dict]:
    if os.path.exists(USERS_DB_FILE):
        try:
            with open(USERS_DB_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
        except Exception as exc:
            print(f"Error loading {USERS_DB_FILE}: {exc}")
            users = {}
    else:
        users = {}

    # Normalize users
    for username, data in users.items():
        role = data.get("role", "user")
        data.setdefault("role", role)

        groups = data.get("groups")
        if isinstance(groups, str):
            groups = [groups]
        if not groups:
            groups = ROLE_TO_GROUPS.get(role, [PUBLIC_GROUP])
        data["groups"] = _ensure_public_group(groups)

        password_hash = data.get("password_hash", "")
        data.setdefault("password_hash", password_hash)
        data.setdefault("must_set_password", False if password_hash else True)
        data.setdefault("disabled", False)
        data.setdefault("name", username)

    return users


USERS: Dict[str, Dict] = load_users()


def save_users() -> None:
    with open(USERS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(USERS, f, indent=2, ensure_ascii=True)


def get_user_groups(username: str) -> List[str]:
    if username in USERS:
        groups = USERS[username].get("groups", [PUBLIC_GROUP])
        if isinstance(groups, str):
            return [groups]
        return groups
    return []


def user_must_set_password(username: str) -> bool:
    if username not in USERS:
        return False
    return bool(USERS[username].get("must_set_password", False))


def set_user_password(username: str, new_password: str) -> None:
    if username not in USERS:
        raise ValueError("Unknown user")
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    USERS[username]["password_hash"] = password_hash
    USERS[username]["must_set_password"] = False
    save_users()


def verify_password(username: str, password: str) -> bool:
    if username not in USERS:
        return False
    if USERS[username].get("disabled"):
        return False
    if USERS[username].get("must_set_password"):
        return False
    password_hash = USERS[username].get("password_hash", "")
    if not password_hash:
        return False
    return password_hash == hashlib.sha256(password.encode()).hexdigest()


def get_user_role(username: str) -> Optional[str]:
    if username in USERS:
        return USERS[username].get("role")
    return None


def is_public_path(file_path: str) -> bool:
    normalized = _normalize_path(file_path)
    for root in PUBLIC_FOLDER_ROOTS:
        if normalized.startswith(_normalize_path(root)):
            return True
    return _matches_any_pattern(normalized, PUBLIC_PATTERNS)


def get_groups_for_folder(file_path: str) -> List[str]:
    normalized = _normalize_path(file_path)
    groups: List[str] = []
    if is_public_path(normalized):
        groups.append(PUBLIC_GROUP)
    for group, roots in GROUP_FOLDER_ROOTS.items():
        for root in roots:
            if normalized.startswith(_normalize_path(root)):
                groups.append(group)
                break
    return list(dict.fromkeys(groups))


def check_folder_access(username: str, folder_path: str) -> bool:
    if username not in USERS:
        return False

    required_groups = get_groups_for_folder(folder_path)
    groups = get_user_groups(username)
    if required_groups:
        return bool(set(groups).intersection(required_groups))

    role = get_user_role(username)
    if role == "admin":
        return True

    # No other group rules defined yet.
    return False


def filter_results_by_user(results: List[Dict], username: str) -> List[Dict]:
    filtered = []
    groups = set(get_user_groups(username))

    for result in results:
        payload = result.get("payload", {})
        allowed_groups = payload.get("allowed_groups")
        file_path = payload.get("sursa_fisier", "")

        if isinstance(allowed_groups, str):
            allowed_groups = [allowed_groups]
        if allowed_groups:
            if groups.intersection(set(allowed_groups)):
                filtered.append(result)
            continue

        if check_folder_access(username, file_path):
            filtered.append(result)

    return filtered


def get_allowed_folders(username: str) -> List[str]:
    user_groups = set(get_user_groups(username))
    folders = list(PUBLIC_FOLDER_ROOTS)
    for group, roots in GROUP_FOLDER_ROOTS.items():
        if group in user_groups:
            folders.extend(roots)
    return folders + PUBLIC_PATTERNS
