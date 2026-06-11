# BPAN Web Application

A web application for generating and managing BPAN (Battery Pack Aadhaar Number) codes for lithium batteries manufactured by Hykon India Limited.

## Technology Stack

| Component    | Technology                         |
|-------------|------------------------------------|
| Frontend    | React 18 + Vite + Tailwind CSS + Zustand |
| Backend     | Python / FastAPI                   |
| Database    | PostgreSQL 15                      |
| Auth        | JWT (HS256) with argon2 password hashing |
| PDF         | ReportLab                          |
| ORM         | SQLAlchemy 2.0                     |
| Migrations  | Alembic                            |
| Container   | Docker + Docker Compose            |

## Quick Start

### Prerequisites

- Docker and Docker Compose

### Running with Docker

```bash
cd BPAN_WEB_APP

# Start all services (a default .env is provided)
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/health

### Initial Setup

On first `docker-compose up`, the seed script automatically:
1. Creates an admin user (credentials from `.env`, default: `admin` / `admin_password`)
2. Seeds lookup tables (years 2025-2033, months A-M, dates 1-27, factory code `9`)
3. Seeds shared entries (country `MD` - India, manufacturer `009` - Hykon India, chemistry `E` - LFP)
4. Creates 10 battery models (HiLIFE and HLH series)
5. Runs database migrations via Alembic

Then:
1. Login as admin at http://localhost:3000/login
2. Populate additional lookup tables via **Admin > Lookup Tables**
3. Create battery models via **Admin > Models** (or use the 10 seeded models)
4. Employees can sign up (username + password, optional role) and await admin approval

### Local Development

```bash
# Backend
uvicorn backend.app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## User Roles

| Role              | Description                                        |
|-------------------|----------------------------------------------------|
| `admin`           | Full system access: manage users, models, lookups  |
| `production_team` | Can create BPANs, search/view/download            |
| `quality_team`    | Read-only: can search/view/download, cannot create |

BPAN creation is restricted to `admin` and `production_team`. `quality_team` users are redirected to the dashboard.

## Project Structure

```
bpan_web_app/
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── endpoints/            # Route handlers (auth, lookup, models, bpan)
│   │   │   └── router.py             # API router aggregator
│   │   ├── core/
│   │   │   ├── config.py             # Environment/settings
│   │   │   ├── database.py           # SQLAlchemy engine & session
│   │   │   ├── security.py           # JWT, password hashing
│   │   │   └── bpan_lookups.py       # Hardcoded code reference tables
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   │   ├── user.py
│   │   │   ├── battery_model.py
│   │   │   ├── bpan.py               # BPAN + AuditLog + SystemConfig
│   │   │   └── lookup.py             # 24 lookup table models
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   ├── services/                 # Business logic
│   │   │   ├── audit.py              # Audit logging
│   │   │   ├── bpan_generator.py     # BPAN code assembly
│   │   │   ├── bpan_decoder.py       # BPAN code decoding
│   │   │   ├── pdf_generator.py      # PDF export
│   │   │   ├── html_generator.py     # HTML detail view
│   │   │   └── qr_parser.py          # QR code parsing (Phase 2)
│   │   └── main.py                   # FastAPI app entry point
│   ├── alembic/                      # Database migrations
│   ├── scripts/seed.py               # Initial data seeding (admin + 10 models)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Layout.jsx            # App shell with navigation + auth guard
│   │   ├── pages/
│   │   │   ├── Login.jsx             # User login
│   │   │   ├── Signup.jsx            # Registration (username + password + role)
│   │   │   ├── Dashboard.jsx         # Dashboard with stats
│   │   │   ├── AdminDashboard.jsx    # User management with approval
│   │   │   ├── BPANCreate.jsx        # BPAN code generation
│   │   │   ├── BPANSearch.jsx        # Search/filter/reports (/bpan/reports)
│   │   │   ├── BPANView.jsx          # View details / PDF export
│   │   │   ├── AdminModels.jsx       # Battery model CRUD
│   │   │   └── AdminLookup.jsx       # Lookup table management (24 tables)
│   │   ├── hooks/
│   │   │   └── useAuthStore.js       # Zustand auth state
│   │   ├── services/
│   │   │   └── api.js                # Axios API client with auto-refresh
│   │   ├── App.jsx                   # Routes & auth guard
│   │   ├── main.jsx                  # React entry point
│   │   └── index.css                 # Tailwind imports
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── package.json
│   └── Dockerfile
├── Docs/
│   ├── PRD.md
│   ├── SRS.md
│   ├── CHANGELOG.md
│   ├── Rough idea of project.md
│   └── Battery Pack Aadhaar Guideline.pdf
├── docker-compose.yml
├── .env
├── pyproject.toml
└── README.md
```

## BPAN Code Structure (21 Characters)

| Position | Field              | Length | Example  | Source                        |
|----------|--------------------|--------|----------|-------------------------------|
| 1-2      | Country Code        | 2      | `MD`     | model.country.code            |
| 3-5      | Manufacturer ID     | 3      | `009`    | model.manufacturer.code       |
| 6-7      | Battery Capacity    | 2      | `AE`     | model.capacity.code           |
| 8        | Battery Chemistry   | 1      | `E`      | model.chemistry.code          |
| 9-10     | Nominal Voltage     | 2      | `BT`     | model.voltage.code            |
| 11-12    | Cell Origin         | 2      | `L`      | model.cell_origin.code        |
| 13       | Extinguisher Class  | 1      | `D`      | model.extinguisher.code       |
| 14       | Manufacturing Year  | 1      | `1`      | (2025)                        |
| 15       | Manufacturing Month | 1      | `D`      | (April)                       |
| 16       | Manufacturing Date  | 1      | `H`      | (17th)                        |
| 17       | Factory Code        | 1      | `9`      | model.factory.code (default)  |
| 18-21    | Serial Number       | 4      | `0307`   | Auto-increment (0000-9999)    |

Letters `I`, `O`, `Q` and digit `0` are excluded from single-character code positions to avoid ambiguity.

### Example

`MD009AEBTDL1DH90307` decodes to: India / Hykon India / 5.12 kWh / LFP / 51.2V / China / Class D / 2025 / April / 17th / Factory 9 / Serial 0307

## Frontend Routes

| Route             | Access                        | Description                     |
|-------------------|-------------------------------|---------------------------------|
| `/login`          | Public                        | Login page                      |
| `/signup`         | Public                        | Registration (username + password + role) |
| `/dashboard`      | Any authenticated user        | Stats and quick actions         |
| `/admin`          | Admin only                    | User approval dashboard         |
| `/bpan/create`    | admin, production_team        | Generate new BPAN               |
| `/bpan/reports`   | Any authenticated user        | Search/filter BPAN records      |
| `/bpan/:code`     | Any authenticated user        | View BPAN details & PDF         |
| `/admin/models`   | Admin only                    | Battery model management        |
| `/admin/lookup`   | Admin only                    | Lookup table management         |

## API Endpoints

### Authentication
| Method | Endpoint                       | Auth   | Description                      |
|--------|--------------------------------|--------|----------------------------------|
| POST   | `/api/v1/auth/signup`          | Public | Register new user                |
| POST   | `/api/v1/auth/login`           | Public | Login (OAuth2 form), get tokens  |
| POST   | `/api/v1/auth/refresh`         | Public | Refresh access token             |
| GET    | `/api/v1/auth/me`              | JWT    | Get current user profile         |
| POST   | `/api/v1/auth/logout`          | JWT    | Logout                           |
| GET    | `/api/v1/auth/users`           | Admin  | List all active users            |
| GET    | `/api/v1/auth/users/pending`   | Admin  | List pending approvals           |
| POST   | `/api/v1/auth/approve/{id}`    | Admin  | Approve or reject a user         |

### Battery Models
| Method | Endpoint                     | Auth     | Description                    |
|--------|------------------------------|----------|--------------------------------|
| GET    | `/api/v1/models/active`      | JWT      | List active models (for BPAN creation) |
| GET    | `/api/v1/models/`            | Admin    | List all models                |
| POST   | `/api/v1/models/`            | Admin    | Create model                   |
| GET    | `/api/v1/models/{id}`        | Admin    | Get model details              |
| PUT    | `/api/v1/models/{id}`        | Admin    | Update model                   |
| DELETE | `/api/v1/models/{id}`        | Admin    | Deactivate model (soft delete) |
| PATCH  | `/api/v1/models/{id}/activate` | Admin | Re-activate model             |

### Lookup Tables
| Method | Endpoint                              | Auth  | Description                   |
|--------|---------------------------------------|-------|-------------------------------|
| GET    | `/api/v1/lookup/tables`               | Auth  | List all 24 table names       |
| GET    | `/api/v1/lookup/{table}`              | Auth  | List entries in a table       |
| POST   | `/api/v1/lookup/{table}`              | Admin | Create entry                  |
| GET    | `/api/v1/lookup/{table}/{identifier}` | Admin | Get single entry              |
| PUT    | `/api/v1/lookup/{table}/{identifier}` | Admin | Update entry                  |
| DELETE | `/api/v1/lookup/{table}/{identifier}` | Admin | Delete entry                  |

### BPAN Operations
| Method | Endpoint                              | Auth     | Description                         |
|--------|---------------------------------------|----------|-------------------------------------|
| GET    | `/api/v1/bpan/models-for-creation`    | JWT      | Active models with decoded values   |
| GET    | `/api/v1/bpan/last-serial`            | JWT      | Current max serial number           |
| GET    | `/api/v1/bpan/stats`                  | JWT      | BPAN counts (today, this_week, last_week, this_month) |
| GET    | `/api/v1/bpan/reports`                | JWT      | Search BPANs with filters (model, date, serial) |
| GET    | `/api/v1/bpan/search`                 | JWT      | Search by partial BPAN code (min 3 chars) |
| POST   | `/api/v1/bpan/generate`               | JWT      | Generate new BPAN                   |
| GET    | `/api/v1/bpan/default-date`           | JWT      | Get default manufacturing date      |
| POST   | `/api/v1/bpan/default-date`           | Admin    | Set default manufacturing date      |
| GET    | `/api/v1/bpan/{code}`                 | JWT      | Get BPAN details                    |
| PUT    | `/api/v1/bpan/{code}`                 | Admin    | Edit BPAN (change model/date)       |
| GET    | `/api/v1/bpan/{code}/pdf`             | JWT      | Download BPAN PDF                   |
| GET    | `/api/v1/bpan/{code}/html`            | JWT      | Get stored HTML view                |
| POST   | `/api/v1/bpan/decode`                 | JWT      | Decode a 21-char BPAN string        |
| POST   | `/api/v1/bpan/qr/parse`               | JWT      | Parse 121-char QR payload           |
| POST   | `/api/v1/bpan/lifecycle/update`       | JWT      | Update battery lifecycle (stub)     |

### Health
| Method | Endpoint              | Auth   | Description                        |
|--------|-----------------------|--------|------------------------------------|
| GET    | `/health`             | Public | `{"status": "healthy", "version": "1.0.0"}` |
| GET    | `/api/v1/health`      | Public | Same as above                      |

## Lookup Tables (24 Tables)

Managed via **Admin > Lookup Tables**:

| Table                        | Code Length | Description                    |
|------------------------------|-------------|--------------------------------|
| countries                    | 2-char      | Country names and regions      |
| manufacturers                | 3-char      | Manufacturer names             |
| battery_capacities           | 2-char      | kWh values                     |
| battery_chemistries          | 1-char      | Chemistry types                |
| nominal_voltages             | 2-char      | Voltage values                 |
| cell_origins                 | 2-char      | Cell origin countries          |
| extinguisher_classes         | 1-char      | Fire extinguisher classes      |
| factory_codes                | 1-char      | Factory identifiers            |
| manufacturing_years          | 1-char      | Year mappings                  |
| manufacturing_months         | 1-char      | Month mappings                 |
| manufacturing_dates          | 1-char      | Day mappings (1-28)            |
| tac_numbers                  | up to 10    | TAC numbers                    |
| cell_types                   | 1-char      | Cell type names                |
| pack_construction_types      | up to 10    | Battery pack construction      |
| module_construction_types    | up to 10    | Module construction            |
| cooling_systems              | 1-char      | Cooling system types           |
| internal_resistances         | up to 10    | Internal resistance (mOhm)     |
| battery_weights              | up to 10    | Weight values (kg)             |
| battery_warranties           | up to 10    | Warranty years                 |
| power_80_soc                 | up to 10    | Power at 80% SoC (kW)          |
| power_20_soc                 | auto ID     | Power at 20% SoC (kW)          |
| carbon_footprints            | up to 10    | Carbon footprint (kgCO2e/kWh)  |
| number_of_cells              | up to 10    | Cell count                     |
| dimensions                   | up to 20    | Length x Width x Height (mm)   |

## Security Features

- JWT access tokens (30 min expiry) with refresh tokens (7 days expiry)
- argon2 password hashing
- Rate limiting on login and signup (5 requests/minute)
- SQLAlchemy ORM (prevents SQL injection)
- Input validation via Pydantic schemas
- CORS origin validation
- Audit logging for key actions (user approval, model changes, lookup changes)

## Environment Variables

Configure via `.env` file at project root:

| Variable                     | Description                    | Default                                       |
|------------------------------|--------------------------------|-----------------------------------------------|
| `DATABASE_URL`               | PostgreSQL connection string   | postgresql://bpan_user:bpan_password@db:5432/bpan_db |
| `POSTGRES_USER`              | PostgreSQL user                | bpan_user                                     |
| `POSTGRES_PASSWORD`          | PostgreSQL password            | bpan_password                                 |
| `POSTGRES_DB`                | PostgreSQL database name       | bpan_db                                       |
| `JWT_SECRET_KEY`             | Secret key for JWT signing     | (change in production)                        |
| `JWT_ALGORITHM`              | JWT algorithm                  | HS256                                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES`| Access token TTL (minutes)     | 30                                            |
| `REFRESH_TOKEN_EXPIRE_DAYS`  | Refresh token TTL (days)       | 7                                             |
| `CORS_ORIGINS`               | Allowed origins (JSON array)   | ["*"]                                         |
| `ADMIN_USERNAME`             | Initial admin username         | admin                                         |
| `ADMIN_PASSWORD`             | Initial admin password         | admin_password                                |
| `INITIAL_SERIAL`             | Starting serial number         | 1                                             |

## License

Proprietary - Hykon India Limited
