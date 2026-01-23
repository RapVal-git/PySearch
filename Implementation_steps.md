# Implementation Steps: Group-Based Document Access Control

## Overview
Implement universal group-based access control so all clients (API + GUI) are gated and users only see/search documents in folders their groups can access.

## Conventions
- Deny-by-default: if a user has no matching allow rule, access is denied.
- Path normalization: normalize to lowercase, consistent separators ("\\"), and trimmed trailing slashes before matching.
- Group resolution: define whether groups come from the token or are loaded from the user store at query time.

---

## Phase 1: Setup & Configuration

### Step 1.1: Unify Auth Module
**File:** `auth_config_advanced.py` (or rename to `auth_config.py` and update imports)
- Consolidate user loading, group membership, and folder filtering logic.
- Fix import issues; ensure no references to missing modules.

### Step 1.2: Extend User Store Schema
**File:** `auth_config_advanced.py` or central auth module

Add user records with group memberships:
```json
{
  "users": {
    "alice": {
      "password_hash": "<sha256>",
      "role": "user",
      "groups": ["finance", "project-a"],
      "name": "Alice Example",
      "disabled": false
    },
    "bob": {
      "password_hash": "<sha256>",
      "role": "user",
      "groups": ["hr"],
      "name": "Bob HR",
      "disabled": false
    }
  }
}
```

### Step 1.3: Define Folder-to-Group Mapping
**File:** `config.py` or `auth_config_advanced.py`

Add folder ACL patterns per group (allow/deny):
```json
{
  "groups": {
    "finance": {
      "allow": ["\\\\Financiar\\\\", "\\\\Facturi\\\\"],
      "deny": ["_hr_"]
    },
    "hr": {
      "allow": ["\\\\HR\\\\", "\\\\Salarii\\\\"],
      "deny": []
    },
    "project-a": {
      "allow": ["\\\\Projects\\\\A\\\\"],
      "deny": []
    },
    "public": {
      "allow": ["\\\\Public\\\\", "_public_"],
      "deny": []
    }
  }
}
```

### Step 1.4: Expose Access Helpers
**File:** `auth_config_advanced.py`
- `get_allowed_folders(username: str) -> list[str]`
- `check_folder_access(username: str, folder_path: str) -> bool`

---

## Phase 2: Indexing With ACL Metadata

### Step 2.1: Extend Chunk Payload Schema
**File:** `generare_vectori_qdrant.py`

Add metadata fields:
```python
payload = {
    "text_chunk": chunk_text,
    "sursa_fisier": file_path,
    "pagina": page_num,
    "tip_document": doc_type,
    "folder_id": extract_folder_id(file_path),
    "allowed_groups": get_groups_for_folder(file_path)
}
```

### Step 2.2: Update Indexing Scripts
**Files:**
- `generare_vectori_qdrant.py`
- `indexare_folder_qdrant.py`
- `indexare_incrementala.py`

Ensure all indexing paths propagate `folder_id` and `allowed_groups` to Qdrant upserts.

### Step 2.3: Update Qdrant Collection Schema
**File:** `cautare_qdrant.py`
- Add indexed fields for `folder_id` and `allowed_groups` in payload schema.
- Ensure Qdrant collection supports filtering on these fields.
- Update any collection initialization to include these fields.

### Step 2.4: Decide Reindex vs Backfill (Required Decision)
- **Option A: Full reindex** from source folders with new schema.
- **Option B: Backfill** existing vectors via Qdrant scroll + update.

Decision criteria:
- Dataset size and acceptable downtime window.
- Availability of original source documents.
- Risk tolerance for partial migration.

Document the choice and exact execution steps.

---

## Phase 3: Query-Time Filtering

### Step 3.1: Update Secured API Search Endpoint
**File:** `api_cautare_secured.py`
1. Authenticate user (existing bearer token logic).
2. Retrieve user groups (token or store).
3. Build Qdrant filter: `allowed_groups` intersects with user groups.
4. Execute Qdrant query with filter.
5. Apply post-retrieval safety check (optional).
6. Return filtered results.

### Step 3.2: Update Secured API Chat Endpoint
**File:** `api_cautare_secured.py`
- Apply same group filtering before passing chunks to `rag_engine.py`.

### Step 3.3: Fix or Retire Open API
**File:** `api_cautare.py`
- **Option A:** Remove or disable public endpoints.
- **Option B:** Route them through secured API with a default `public` group.

Document the choice clearly.

### Step 3.4: Update GUI Search/Chat
**File:** `gui_cautare.py`
- **Preferred:** route all GUI queries through secured API.
- Remove any direct Qdrant access that bypasses filtering.

---

## Phase 4: User/Group Management

### Step 4.1: Update User Import Script
**File:** `import_sap_users.py`
- Parse SAP user data and extract group/department mappings.
- Populate `groups` field in user records.
- Example: SAP cost center -> group name.

### Step 4.2: Update User Management CLI
**File:** `manage_users.py`
- Add commands to assign/revoke groups per user.
- Validate group names against configured ACL groups.
- Support bulk import with group mappings.

### Step 4.3: Documentation
Create or update:
- Group assignment procedures.
- Folder-to-group mapping maintenance guide.
- Token refresh/expiry policy (if changed).

---

## Phase 5: Testing & Migration

### Step 5.1: Unit Tests
**File:** `test_demo/test_group_access.py`
Test cases:
- User with multiple groups sees union of allowed folders.
- Deny rules override allow rules.
- Invalid group denies access.
- Qdrant filter correctly matches payload.

### Step 5.2: Integration Tests
**File:** `test_demo/test_api_group_gating.py`
Test cases:
- Secured API filters results by user groups.
- GUI shows only allowed documents.
- Open API (if active) respects group rules.

### Step 5.3: Data Migration
Steps:
- Execute the chosen reindex/backfill plan.
- Schedule downtime if needed.
- Validate vector count and sample results post-migration.
- Audit user group assignments before go-live.

### Step 5.4: Rollback Plan
Document:
- How to restore from backup if needed.
- How to disable group filtering in emergency (with audit logging).

---

## Phase 6: Deployment & Monitoring

### Step 6.1: Configuration Management
- Version control group/folder mapping.
- Document config change procedures.
- Set up config hot-reload or restart procedures.

### Step 6.2: Logging & Audit
Add logging for:
- User authentication attempts.
- Access denied (wrong group).
- Folder access changes.
- Reindex/backfill operations.

### Step 6.3: Health Checks
- Verify Qdrant filters work correctly.
- Monitor token validity.
- Alert on auth failures.

---

## Summary Table
| Phase | Files | Key Actions | Effort |
|---|---|---|---|
| 1. Setup | `auth_config_advanced.py`, `config.py` | User schema, folder ACL, unify auth | Low |
| 2. Indexing | `generare_vectori_qdrant.py`, `cautare_qdrant.py` | Add payload fields, update schema, reindex | Medium |
| 3. Query | `api_cautare_secured.py`, `gui_cautare.py` | Add Qdrant filters, post-checks | Medium |
| 4. Users | `import_sap_users.py`, `manage_users.py` | Group assignment, import integration | Low |
| 5. Testing | New test files | Unit/integration tests, migration validation | Medium |
| 6. Deploy | Multiple files | Config, logging, monitoring, rollback | Low |

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Reindex downtime | Schedule during low-usage window; plan backfill strategy |
| Existing tokens invalid after schema change | Keep old tokens valid for grace period or force re-auth |
| Missing group in user record | Deny access by default; require explicit allow |
| Qdrant filter misconfigured | Test filters in staging; audit sample results |
| GUI still bypasses auth | Force routing through API; remove direct Qdrant calls |

## Sign-Off Checklist
- User groups loaded from store and passed to all query paths.
- Qdrant payloads include `folder_id` and `allowed_groups` for all documents.
- All clients (API, GUI) enforce group filters before returning results.
- Open API retired or wrapped through secured API.
- Unit and integration tests pass.
- Audit logging active.
- User/group documentation ready.
- Rollback procedure tested.
- Deployed to staging and validated.

---

## Current Gaps Observed
- `api_cautare_secured.py` imports an `auth_config` module that does not exist and does not use `auth_config_advanced.py`.
- `indexare_incrementala.py` only writes basic payload metadata; no `folder_id` / `allowed_groups` are added.
- `gui_cautare.py` queries Qdrant directly and bypasses secured API filtering.

## Quick Sync Plan (Minimum Alignment)
1. Unify auth: rename/import `auth_config_advanced.py` as the main module and expose `get_allowed_folders` / `check_folder_access`.
2. Extend indexing: add `folder_id` + `allowed_groups` to payload in `indexare_incrementala.py` and `generare_vectori_qdrant.py`.
3. Update Qdrant: add payload indexes for `allowed_groups` in `cautare_qdrant.py`.
4. Secure API: build Qdrant filter on `allowed_groups` in `api_cautare_secured.py` (not only post-filter).
5. Route GUI: `gui_cautare.py` uses secured API only.
6. Add minimal tests: one unit test + one API happy-path test.

## Immediate Decision Needed
Decide now whether to do full reindex or backfill, and document the steps plus rollback.
