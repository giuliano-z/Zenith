# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Zenith is a personal-finance API (accounts, transactions, balances) — Django + DRF backend, with a planned React + TypeScript frontend (not yet created). The spec and decision records live in `docs/`: `docs/F1_srs.md` (full SRS, the source of the `RF-xxx`/`RNF-xxx`/`RS-xxx` requirement IDs referenced throughout the code) and `docs/F2_adr/` (architecture decision records, ADR-001..005). When code cites an ID like `RS-004` or `ADR-004`, the rationale is in those files.

The code, comments, docstrings, and commit messages are in **Spanish (es-AR)**. Match that — write new comments/docstrings and commit messages in Spanish.

## Commands

All backend commands run from `backend/` (the CI sets `working-directory: backend`). A local venv lives at `backend/.venv`.

```bash
cd backend

# Run the full test suite (pytest, configured via pytest.ini)
pytest

# Run one app, one file, one test
pytest apps/transactions/
pytest apps/transactions/tests/test_views.py
pytest apps/transactions/tests/test_views.py -k test_create_transfer

# Lint (must pass clean — CI gates on it)
ruff check .
ruff check . --fix

# Security scan (same flags as CI)
bandit -r apps config -ll

# DB migrations
python manage.py makemigrations
python manage.py migrate

# Dev server (needs Postgres running + .env)
python manage.py runserver
```

Full stack via Docker (Postgres on host port **5433**, backend on 8000):

```bash
docker compose up   # from repo root
```

`.env` is required (copy `.env.example`). `DJANGO_SETTINGS_MODULE` defaults to `config.settings.development`; tests and CI use the same development settings.

## Architecture

**Layered (Clean Architecture, pragmatic Django flavor) — see ADR-003.** Each domain module under `backend/apps/<module>/` is split by responsibility, and the rule that defines the codebase is:

- **`services.py` = domain layer. It never touches HTTP** (no function takes a `Request`) — this is RNF-006, and it's why services are unit-testable in isolation. All business logic lives here.
- **`views.py` = presentation layer. Views only orchestrate**: validate input with a serializer, call `services`, shape the response. No business rules in views.
- **`serializers.py`** validates/serializes; **`models.py`** is persistence. Modules are kept small by RNF-007 (≤400 lines/module, ≤50 lines/function) — respect this when adding code.

Apps: `users` (auth), `accounts`, `transactions`, `common` (shared helpers: `pagination.py`, `exceptions.py`, `utils.py`). Settings split into `config/settings/{base,development,production}.py`. Each app's URLs are wired in `config/urls.py` under `/api/<module>/`.

### Cross-cutting invariants (don't break these)

- **User isolation (RNF-005, RS-004).** Every query in a service filters by `user`. A resource that belongs to another user must return **403, never 404** — a 404 would confirm the resource exists and allow enumeration. Account ownership is the single source of truth: `accounts.services.get_account_detail` raises `AccountNotFoundError` (→404) or `AccountAccessDeniedError` (→403), and `transactions.services` re-exports those same exception symbols rather than re-implementing the check. Views translate them (see `transactions/views.py:_forbidden`).

- **Auth.** django-knox, opaque DB tokens, 24h TTL (ADR-002). DRF defaults are global: `IsAuthenticated` everywhere (missing token → 401) and knox `TokenAuthentication`. Identity is by **email** via a custom `users.User` (`AUTH_USER_MODEL`). Passwords use Argon2id (RNF-003). Login returns a generic 401 with no user enumeration (RS-002).

- **Balance model (ADR-004).** `balance = account.initial_balance + Σ(active transactions, date ≤ cutoff)`. The signed sum lives in `transactions.services.get_transaction_sum_for_account` (income/transfer_in add, expense/transfer_out subtract; `amount` is always stored positive, the type decides the sign). `as_of_date` clips future-dated rows — this is how installment purchases only hit the balance as each monthly installment comes due. `accounts.services` imports this function **locally inside the function body** to avoid the accounts ↔ transactions circular import; keep that pattern.

- **Transfers and installments are atomic.** `create_transfer` writes a linked `TRANSFER_OUT`/`TRANSFER_IN` pair (`transfer_pair`), `create_installment` writes N `EXPENSE` rows — both wrapped in `@db_transaction.atomic`. Transfers do **not** go through `create_transaction`; they have their own service so the paired creation is guaranteed.

## Conventions

- Code/comments/docstrings/commits in Spanish; reference the relevant `RF/RNF/RS/ADR/CU` ID when a piece of code exists to satisfy one.
- Ruff config (`pyproject.toml`): line length 100, rule sets `E,F,I,B,S,UP`, migrations excluded. Tests may use `assert` and test passwords (S101/S105/S106 ignored under `tests/`). Bandit runs on `apps` + `config`.
- New domain logic goes in `services.py`, not views. New endpoints get a serializer for input validation. Add tests under the app's `tests/` (`test_services.py` for domain, `test_views.py` for endpoints).

## Design system (frontend, when it gets built)

`CLAUDE.austral.md` is the **AUSTRAL design system** — a dark-only React/Tailwind/shadcn visual spec (palette, typography, component patterns) shared across Giuliano's projects. Read it before generating any UI: never hardcode hex (use the Tailwind theme classes), celeste is the only chromatic accent, Framer Motion for animation.
