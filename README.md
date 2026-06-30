# SecureBank

A production-grade, 3-tier banking API and dashboard. SecureBank lets users
register, authenticate, open bank accounts, deposit and withdraw money, and
review their transaction history — with security controls appropriate for a
fintech application (RS256 JWTs, refresh-token rotation and blacklisting,
bcrypt password hashing, and Fernet encryption of balances at rest).

- **Frontend:** React (Vite), plain CSS modules, Axios
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy 2.0, Pydantic v2
- **Database:** PostgreSQL (SQLite is used automatically for the test suite)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                              Browser (SPA)                             │
│  React + Vite                                                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌────────────────────┐  │
│  │  Login /  │  │ Dashboard │  │  Account  │  │  Axios apiClient    │  │
│  │ Register  │  │ (accounts)│  │  detail   │  │  (refresh interceptor)│ │
│  └───────────┘  └───────────┘  └───────────┘  └────────────────────┘  │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │  HTTPS + httpOnly cookies (JWT)
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          FastAPI backend                               │
│                                                                        │
│   routes/  ──►  services/  ──►  models/ (SQLAlchemy ORM)               │
│     auth        auth_service       User / Account / Transaction         │
│     accounts    account_service    RefreshToken                         │
│     transactions transaction_service                                    │
│                                                                        │
│   core/     security (RS256 JWT, bcrypt)   encryption (Fernet)         │
│             dependencies (auth guard)      middleware (X-Request-ID)   │
│             rate_limit (slowapi)                                        │
│   schemas/  Pydantic v2 strict validation                              │
└───────────────────────────────┬──────────────────────────────────────┘
                                 │  SQLAlchemy ORM (no raw SQL)
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                            PostgreSQL                                  │
│   users · accounts (encrypted_balance) · transactions · refresh_tokens │
└──────────────────────────────────────────────────────────────────────┘
```

The three tiers are cleanly separated. Within the backend, responsibilities are
split further: **routes** handle HTTP, **services** hold business logic,
**models** define persistence, **schemas** validate I/O, and **core** holds
cross-cutting security primitives. No file exceeds 200 lines.

---

## Prerequisites

- **Python** 3.11 or newer
- **Node.js** 18 or newer (tested on 20)
- **PostgreSQL** 13 or newer
- **OpenSSL** (for generating the RSA key pair)

---

## Setup

### 1. Clone and create the database

```bash
createdb securebank          # or: psql -c "CREATE DATABASE securebank;"
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Generate cryptographic keys

The backend signs JWTs with an RSA key pair (RS256) and encrypts balances with
a Fernet key. Generate all of them with the helper script:

```bash
chmod +x generate_keys.sh
./generate_keys.sh
```

This writes `keys/private.pem` and `keys/public.pem`, and prints an
`ENCRYPTION_KEY=...` line to copy into your `.env`.

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`: set `DATABASE_URL` to your PostgreSQL instance and paste the
`ENCRYPTION_KEY` printed by `generate_keys.sh`. See
[Environment variables](#environment-variables) below for every setting.

### 5. Run the backend

```bash
uvicorn app.main:app --reload --port 8000
```

The API is now at `http://localhost:8000`. Tables are created automatically on
startup.

### 6. Frontend

```bash
cd ../frontend
npm install
cp .env.example .env               # optional; defaults to http://localhost:8000
npm run dev
```

Open `http://localhost:5173`.

> **Local cookies:** auth tokens are delivered as `httpOnly` cookies. Browsers
> only store `Secure` cookies over HTTPS, so keep `DEBUG=true` in the backend
> `.env` for local development (the example file already does). In production,
> set `DEBUG=false` and serve the API over HTTPS.

---

## Generating keys

`generate_keys.sh` produces everything the app needs:

| Output | Purpose |
| --- | --- |
| `keys/private.pem` | RSA private key — signs JWTs (RS256) |
| `keys/public.pem` | RSA public key — verifies JWTs |
| `ENCRYPTION_KEY` (printed) | Fernet key — encrypts account balances at rest |

Keys live under `backend/keys/` and are git-ignored. Never commit them.

---

## Seed data

Populate the database with demo users, accounts and transactions:

```bash
cd backend
python -m app.utils.seed
```

This creates **3 users**, **2 accounts each**, and **10 random transactions per
account**, then prints the login credentials. All demo users share the password
`Demo!Pass123`:

| Email | Password |
| --- | --- |
| alice@example.com | `Demo!Pass123` |
| bob@example.com | `Demo!Pass123` |
| carol@example.com | `Demo!Pass123` |

> The seed script resets the demo tables on each run.

---

## Running tests

The test suite runs against an isolated, file-backed SQLite database and
generates its own throwaway keys, so no PostgreSQL or `.env` is required.

```bash
cd backend
pytest
```

Coverage includes registration (success, duplicate email, weak password), login
(success, wrong password, inactive user), account creation/retrieval/deletion,
deposits and withdrawals (success, insufficient funds, negative and over-limit
amounts), transaction history, and JWT refresh/rotation and logout.

---

## API documentation

FastAPI auto-generates interactive docs once the backend is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoints

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Create a new user |
| `POST` | `/auth/login` | Authenticate, receive token cookies |
| `POST` | `/auth/refresh` | Rotate the refresh token into a new pair |
| `POST` | `/auth/logout` | Revoke (blacklist) the refresh token |
| `POST` | `/accounts` | Open a new account |
| `GET` | `/accounts` | List the user's accounts |
| `GET` | `/accounts/{id}` | Retrieve one account |
| `DELETE` | `/accounts/{id}` | Close an empty account |
| `POST` | `/accounts/{id}/deposit` | Deposit money |
| `POST` | `/accounts/{id}/withdraw` | Withdraw money |
| `GET` | `/accounts/{id}/transactions` | Transaction history |

---

## Environment variables

All backend configuration comes from the environment (or `.env`) — nothing is
hardcoded.

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy connection string, e.g. `postgresql://user:password@localhost:5432/securebank` |
| `SECRET_KEY` | Generic application secret for miscellaneous signing |
| `PRIVATE_KEY_PATH` | Path to the RSA private key (JWT signing) |
| `PUBLIC_KEY_PATH` | Path to the RSA public key (JWT verification) |
| `ENCRYPTION_KEY` | Fernet key encrypting account balances at rest |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access-token lifetime (default `15`) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh-token lifetime (default `7`) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins (the React dev server) |
| `MAX_TRANSACTION_AMOUNT` | Maximum amount per deposit/withdrawal |
| `DEBUG` | `true` for local dev (non-Secure cookies, verbose errors); `false` in production |

Frontend (`frontend/.env`):

| Variable | Description |
| --- | --- |
| `VITE_API_URL` | Backend base URL (default `http://localhost:8000`) |

---

## Security features

**Password security**
- Passwords are hashed with **bcrypt**; plaintext is never stored.
- A strength policy (length + upper/lower/digit/special) is enforced by both the
  Pydantic schema and the frontend.

**JWT authentication**
- **RS256 (asymmetric)** signing: the private key signs, the public key verifies.
- Short-lived **access tokens** (15 min) and long-lived **refresh tokens** (7 days).
- **Rotation:** every refresh revokes the old token and issues a new pair.
- **Blacklisting:** only a SHA-256 hash of each refresh token is stored, and
  logout marks it revoked so it can never be reused.

**Sensitive data encryption**
- Account balances are encrypted at rest with **Fernet** symmetric encryption.
- The key is supplied via `ENCRYPTION_KEY` and never appears in code.
- Plaintext balances exist only in memory while a transaction is processed.

**Input validation**
- Strict **Pydantic v2** schemas validate every request.
- Deposits/withdrawals must be strictly positive and below `MAX_TRANSACTION_AMOUNT`.
- All database access goes through the **SQLAlchemy ORM** — no raw SQL, so
  parameterization prevents SQL injection.

**API security**
- **Rate limiting** (slowapi) throttles the auth endpoints against brute force.
- **CORS** is restricted to the configured origins, with credentials enabled.
- An **`X-Request-ID`** header is attached to every response for audit trails.
- Tokens are delivered as **`httpOnly` cookies**, keeping them out of reach of
  JavaScript (and therefore XSS).

---

## Project structure

```
securebank/
├── frontend/        React (Vite) SPA — pages, components, services, utils
├── backend/         FastAPI app — routes, services, models, schemas, core, utils
│   ├── tests/       pytest suite (SQLite-backed fixtures)
│   ├── generate_keys.sh
│   └── .env.example
└── README.md
```
