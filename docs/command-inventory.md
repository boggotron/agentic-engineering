# Repository command inventory

## Authoritative commands

| Command | Applicability | Prerequisite | Expected evidence |
| --- | --- | --- | --- |
| `python scripts/test_validate_repository.py` | All repository changes | Python 3.11+ | `unittest` exits 0. |
| `python scripts/validate_repository.py` | All repository changes | Python 3.11+ | `Repository validation passed.` |
