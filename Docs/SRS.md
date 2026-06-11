# BPAN Web Application - Software Requirements Specification (SRS)

**Version**: 1.0  
**Date**: May 12, 2026  
**Project**: BPAN Battery Management System  
**For**: Hykon India Limited

---

## 1. Introduction

### 1.1 Purpose

This document provides a detailed Software Requirements Specification for the BPAN (Battery Pack Aadhaar Number) Web Application. The system enables Hykon India Limited to generate, manage, and track unique 21-character alphanumeric codes for lithium batteries produced at their manufacturing facility.

### 1.2 Scope of Work

The system shall:
- Provide secure authentication with role-based access control (Admin/Employee)
- Enable Admin users to manage lookup tables, battery models, and user accounts
- Enable Employee users to generate BPAN codes through a guided workflow
- Generate PDF and HTML exports of BPAN data
- Provide reporting functionality for BPAN generation statistics

### 1.3 Target Users

| User Type | Description |
|-----------|-------------|
| Admin | Hykon IT/Management staff who configure models, tables, and approve users |
| Employee | Factory floor staff who generate BPAN codes for batteries |

---

## 2. Functional Requirements

### 2.1 Authentication Module

#### FR-AUTH-001: User Registration
- Users can self-register with username, email, and password
- Default role is 'employee'
- Registration creates user with `is_approved = false`
- User must wait for admin approval before login

#### FR-AUTH-002: User Login
- Users provide username/email and password
- On successful auth, JWT access token (30min) and refresh token (7 days) returned
- On failure: "Invalid credentials" error shown

#### FR-AUTH-003: User Approval Workflow
- Admin can view list of pending users via dashboard
- Admin can approve or reject any pending user
- On approval: user `is_approved = true`, user can login
- On rejection: user `is_active = false`, cannot login
- No email integration required (dashboard-only approval)

#### FR-AUTH-004: Token Refresh
- Client can exchange valid refresh token for new access token
- Invalid/expired refresh tokens rejected with 401

#### FR-AUTH-005: Password Security
- Minimum 8 characters required
- Passwords hashed with argon2 (memory: 64MB, iterations: 3, parallelism: 4)
- Salt: 16 bytes random per password

### 2.2 Lookup Tables Module

#### FR-LOOKUP-001: Table Listing
- Admin can list all lookup table names
- Response includes table metadata

#### FR-LOOKUP-002: Table Entries CRUD
- Admin can create new entry with unique code
- Admin can read single entry by code
- Admin can update entry (code cannot be changed)
- Admin can delete entry

#### FR-LOOKUP-003: Bulk Import
- Admin can upload CSV file to bulk import entries
- CSV format: code,name,description (header row required)
- Invalid rows logged, valid rows imported in transaction
- Returns count of imported and failed rows

#### FR-LOOKUP-004: Tables Required
| Table Name | Code Length | Description |
|-----------|-------------|-------------|
| countries | 2 chars | Country codes and names |
| manufacturers | 3 chars | Manufacturer identifiers |
| battery_capacities | 2 chars | Battery capacity in kWh |
| battery_chemistries | 1 char | Chemistry type codes |
| nominal_voltages | 2 chars | Voltage values |
| cell_origins | 2 chars | Cell origin countries |
| extinguisher_classes | 1 char | Fire extinguisher classes |
| factory_codes | 1 char | Factory identifiers |
| manufacturing_years | 1 char | Year code mapping |
| manufacturing_months | 1 char | Month code mapping |
| manufacturing_dates | 1 char | Date code mapping |
| tac_numbers | varies | TAC number codes |
| cell_types | 1 char | Cell type names |
| construction_types | varies | Construction type names |
| cooling_systems | 1 char | Cooling system types |

**Character Restriction**: The letter **`I`** is excluded from all single-character code fields following the international standard for vehicle/battery identification codes (similar to VIN standards) to avoid ambiguity with the number `1`.

### 2.3 Battery Models Module

#### FR-MODEL-001: Create Model
- Admin creates battery model with all required fields
- All constant values linked to lookup tables
- All variable values stored directly
- Validation: required lookup FKs must exist

#### FR-MODEL-002: List Models
- Admin sees all models (active and inactive)
- Employee sees only active models
- Response includes decoded values for readability

#### FR-MODEL-003: Update Model
- Admin can modify any model field
- Changing lookup FKs must validate target exists

#### FR-MODEL-004: Deactivate Model
- Admin can soft-delete (set `is_active = false`)
- Inactive models not shown in employee dropdown
- Existing BPANs with this model remain valid

#### FR-MODEL-005: Model Fields

**Constant (per model - linked to lookups):**
| Field | Type | Lookup Table |
|-------|------|-------------|
| country_code | FK | countries |
| manufacturer_code | FK | manufacturers |
| capacity_code | FK | battery_capacities |
| chemistry_code | FK | battery_chemistries |
| voltage_code | FK | nominal_voltages |
| cell_origin_code | FK | cell_origins |
| extinguisher_code | FK | extinguisher_classes |
| factory_code | FK | factory_codes |
| tac_code | FK | tac_numbers |
| cell_type_code | FK | cell_types |
| pack_construction_code | FK | construction_types |
| module_construction_code | FK | construction_types |
| cooling_code | FK | cooling_systems |
| internal_resistance | DECIMAL | - |
| warranty_years | INTEGER | - |

**Variable (per model - stored directly):**
| Field | Type |
|-------|------|
| num_cells | INTEGER |
| weight_kg | DECIMAL |
| length_mm | INTEGER |
| width_mm | INTEGER |
| height_mm | INTEGER |
| power_80_soc | DECIMAL |
| power_20_soc | DECIMAL |
| carbon_footprint | DECIMAL |

### 2.4 BPAN Generation Module

#### FR-BPAN-001: Get Models for Creation
- Employee sees list of active battery models
- Response includes: model name, capacity, chemistry (decoded)

#### FR-BPAN-002: Generate BPAN
- Employee selects model
- System auto-populates:
  - Manufacturing date (server current date)
  - Serial number (auto-increment globally across all products)
- Employee verifies displayed info
- On Generate:
  1. System assembles 21-char code
  2. System stores BPAN record with full HTML
  3. Returns success with full BPAN code

#### FR-BPAN-003: BPAN Code Assembly
```
Position : Field
1-2      : Country Code
3-5      : Manufacturer Code
6-7      : Battery Capacity Code
8        : Battery Chemistry Code
9-10     : Nominal Voltage Code
11-12    : Cell Origin Code
13       : Extinguisher Class Code
14       : Manufacturing Year Code
15       : Manufacturing Month Code
16       : Manufacturing Date Code
17       : Factory Code
18-21    : Serial Number (4-digit zero-padded)
```

#### FR-BPAN-004: Serial Number Logic
- Format: `0001` to `9999`
- Auto-increment per day per factory
- Resets at midnight (server time)
- Unique constraint: (model_id, factory_code, date, serial_number)

#### FR-BPAN-005: Retrieve BPAN
- Employee enters 21-char code
- System returns:
  - All encoded values (decoded)
  - Model details
  - Full HTML representation
  - Created by and timestamp

#### FR-BPAN-006: Export PDF
- Employee requests PDF for BPAN code
- System generates PDF with:
  - BPAN code in large readable font
  - All decoded fields
  - Manufacturing info
  - Model specifications
  - Generation timestamp
- Returns downloadable PDF file

#### FR-BPAN-007: Export HTML
- Employee requests HTML view
- System returns full HTML page with embedded styles
- All battery data displayed in structured format

### 2.5 Reports Module

#### FR-REPORT-001: Today's BPANs
- Admin sees count and list of BPANs created today
- Includes: code, model, created_by, timestamp

#### FR-REPORT-002: This Week's BPANs
- Admin sees count and list of BPANs created this week
- Week defined as Monday-Sunday

#### FR-REPORT-003: This Month's BPANs
- Admin sees count and list of BPANs created this month

#### FR-REPORT-004: Historical Report
- Admin sees paginated list of all BPANs
- Sorted by creation date (newest first)
- Pagination: 50 per page

### 2.6 Date Change Requests Module

#### FR-DATE-001: Submit Request
- Employee can request manufacturing date change
- Must provide: requested_date, reason
- Creates request with `status = pending`

#### FR-DATE-002: Process Request
- Admin sees list of pending requests
- Admin can approve or reject
- On approve: employee can use new date for BPAN generation
- On reject: admin provides notes, employee notified

---

## 3. Non-Functional Requirements

### 3.1 Performance

| Metric | Requirement |
|--------|-------------|
| API Response Time | < 500ms for single resource APIs |
| BPAN Generation | < 1s end-to-end |
| PDF Generation | < 3s |
| Concurrent Users | Support 50 simultaneous users |

### 3.2 Security

| Requirement | Implementation |
|------------|----------------|
| Password Storage | argon2-cffi with salt |
| JWT Algorithm | HS256, 30min access token |
| SQL Injection Prevention | SQLAlchemy ORM (parameterized) |
| Input Validation | Pydantic schemas |
| Rate Limiting | 5 failed logins → 15min lockout per IP |
| HTTPS | Required in production |
| CORS | Configurable origin whitelist |
| Audit Logs | All admin actions logged with user, timestamp, action |

### 3.3 Availability

- Application designed for 99% uptime during working hours
- Local Docker deployment for company server

### 3.4 Scalability

- Horizontal scaling via Docker Compose with multiple backend instances
- Database connection pooling (default: 10 connections)
- Stateless API design for load balancer compatibility

### 3.5 Maintainability

- Alembic migrations for database schema versioning
- Modular project structure
- Comprehensive API documentation via OpenAPI/Swagger
- Separation of schemas, models, services, and endpoints

---

## 4. Technical Architecture

### 4.1 System Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              Docker Network              │
  ┌──────────────┐  │  ┌─────────────┐  ┌────────────────────┐  │
  │   Browser   │←→│  │  NGINX      │  │   FastAPI Backend  │  │
  │  (React SPA)│  │  │  (:80/:443) │←→│   (uvicorn:8000)   │  │
  └──────────────┘  │  └─────────────┘  └────────────────────┘  │
                    │                            │               │
                    │                            ↓               │
                    │                   ┌────────────────────┐  │
                    │                   │   PostgreSQL       │  │
                    │                   │   (:5432)          │  │
                    │                   └────────────────────┘  │
                    └─────────────────────────────────────────┘
```

### 4.2 Backend Technology Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Framework | FastAPI | REST API framework |
| ORM | SQLAlchemy 2.0 | Database operations |
| Migrations | Alembic | Schema versioning |
| Validation | Pydantic | Request/response schemas |
| Auth | PyJWT + python-jose | JWT token handling |
| Password | argon2-cffi | Secure password hashing |
| PDF | ReportLab | PDF generation |
| CORS | fastapi.middleware.cors | Cross-origin config |
| Rate Limit | slowapi | Rate limiting |

### 4.3 Frontend Technology Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Framework | React 18 | UI framework |
| Routing | React Router v6 | SPA navigation |
| State | Zustand | Lightweight state management |
| HTTP | Axios | API communication |
| Styling | Tailwind CSS | Utility-first CSS |
| Forms | React Hook Form | Form handling |
| PDF | jsPDF | Client-side PDF (optional) |

### 4.4 Database Schema (PostgreSQL)

```sql
-- Core tables defined per PRD Section 5.1
-- All UUID primary keys
-- All timestamps with timezone
-- Soft deletes where applicable
-- Indexes on: code fields, foreign keys, created_at
```

### 4.5 API Documentation

- OpenAPI 3.0 specification
- Swagger UI at `/docs`
- ReDoc at `/redoc`
- All endpoints documented with request/response schemas

---

## 5. Data Flow Diagrams

### 5.1 BPAN Generation Flow

```
Employee                    Backend                      Database
   │                           │                            │
   │──Select Model────────────→│                            │
   │←─Model Details────────────│                            │
   │                           │                            │
   │──Verify + Generate────────│                            │
   │                           │──Fetch next serial#────────→│
   │                           │←─serial: 0001──────────────│
   │                           │                            │
   │                           │──Insert BPAN──────────────→│
   │                           │←─success───────────────────│
   │←─21-char BPAN─────────────│                            │
   │                           │                            │
   │──Request PDF────────────→│                            │
   │                           │──Generate PDF──────────────→│
   │                           │←─PDF bytes──────────────────│
   │←─PDF download────────────│                            │
```

### 5.2 User Registration Flow

```
User                    Backend                   Admin Dashboard
   │                       │                          │
   │──Signup──────────────→│                          │
   │←─Pending approval─────│                          │
   │                       │                          │
   │                       │     (Admin reviews)      │
   │                       │←─────────────────────────│
   │                       │                          │──View pending users
   │                       │                          │──Click Approve
   │                       │←─Approve─────────────────│
   │                       │                          │
   │──Login (if approved)→│                          │
   │←─JWT tokens───────────│                          │
```

---

## 6. API Contracts

### 6.1 Authentication Endpoints

#### POST /api/v1/auth/signup
**Request:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
**Response (201):**
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string",
  "role": "employee",
  "is_approved": false,
  "message": "Registration pending approval"
}
```

#### POST /api/v1/auth/login
**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Response (200):**
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer"
}
```

### 6.2 BPAN Endpoints

#### POST /api/v1/bpan/generate
**Request:**
```json
{
  "model_id": "uuid",
  "factory_code": "string",
  "custom_date": "date (optional)"
}
```
**Response (201):**
```json
{
  "id": "uuid",
  "code_21char": "MY009A6FKKKLC1DH80001",
  "model_name": "HiLife 12.8",
  "manufacturing_date": "2025-04-17",
  "serial_number": "0001",
  "created_at": "timestamp"
}
```

### 6.3 Error Response Format
```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "errors": []
}
```

---

## 7. Acceptance Criteria

### 7.1 Authentication

- [ ] User can signup and receive pending approval status
- [ ] Admin can view pending users via dashboard
- [ ] Admin can approve user, user can then login
- [ ] Admin can reject user, user cannot login
- [ ] Approved user can login and receive JWT tokens
- [ ] Unapproved user cannot login
- [ ] Invalid credentials return 401
- [ ] Expired tokens are rejected

### 7.2 Lookup Tables

- [ ] Admin can CRUD all lookup tables via API
- [ ] Non-admin cannot access lookup endpoints
- [ ] Bulk CSV import correctly imports valid rows
- [ ] Bulk CSV import reports failed rows

### 7.3 Battery Models

- [ ] Admin can create model with all required fields
- [ ] Admin can update existing model
- [ ] Admin can deactivate model
- [ ] Employee can list active models only
- [ ] Model creation validates all FK lookups exist

### 7.4 BPAN Generation

- [ ] Employee can view available models
- [ ] System auto-fills current date and next serial number
- [ ] Generated BPAN is exactly 21 characters
- [ ] BPAN correctly encodes all selected model values
- [ ] Same model+date combo does not duplicate serial numbers
- [ ] Employee can search BPAN by code
- [ ] Employee can download PDF with full details
- [ ] Employee can view HTML representation

### 7.5 Reports

- [ ] Admin can view today's BPAN count
- [ ] Admin can view this week's BPAN count
- [ ] Admin can view this month's BPAN count
- [ ] Admin can paginate through historical BPANs

### 7.6 Security

- [ ] Passwords are hashed with argon2
- [ ] SQL injection is not possible via API inputs
- [ ] Rate limiting blocks after 5 failed logins
- [ ] All admin actions are logged
- [ ] CORS only allows configured origins

---

## 8. Project Deliverables

| Item | Description |
|------|-------------|
| backend/ | FastAPI application with all endpoints |
| frontend/ | React SPA with all pages |
| docker-compose.yml | Complete stack for local deployment |
| docs/ | PRD and SRS documentation |
| scripts/ | Database seed script for admin user |

---

## 9. Deployment Requirements

### 9.1 Environment Variables

```env
# Database
DATABASE_URL=postgresql://bpan_user:bpan_pass@localhost:5432/bpan_db

# JWT
JWT_SECRET_KEY=<32-byte-random-string>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email (Resend)
RESEND_API_KEY=<your-resend-api-key>
EMAIL_FROM=noreply@hykonindia.com

# CORS
CORS_ORIGINS=http://localhost:3000,https://bpan.hykonindia.com

# Admin Seed
ADMIN_USERNAME=<admin_username>
ADMIN_EMAIL=<admin_email>
ADMIN_PASSWORD=<admin_password>
```

### 9.2 Docker Requirements

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

---

## 10. Future Considerations (Phase 2+)

| Feature | Priority | Notes |
|---------|----------|-------|
| QR Code Generation | High | Encode BMCS and BCF data |
| Hykon Branding | Medium | Custom PDF template |
| Bulk BPAN Generation | Medium | CSV upload for batch creation |
| Mobile Responsive UI | Medium | Optimize for tablets |
| Battery Lifecycle Tracking | Low | Real-time health updates |
| Multi-language Support | Low | i18n for factory workers |

---

## 11. Appendix

### A. BPAN Code Example

**Character Restriction Note**: The letter **`I`** is excluded from single-character code positions (8, 13, 14, 15, 16, 17) following international vehicle/battery code standards to avoid ambiguity with the number `1`.

For the code `MY009A6FKKKLC1DH80001`:

| Position | Value | Decoded |
|----------|-------|---------|
| 1-2 | MY | India |
| 3-5 | 009 | Hykon India Limited |
| 6-7 | A6 | 30 kWh |
| 8 | F | NMC (Nickel Manganese Cobalt) |
| 9-10 | KK | 307V |
| 11-12 | KL | Korea |
| 13 | C | Class C |
| 14 | 1 | 2025 |
| 15 | D | April |
| 16 | H | 17th |
| 17 | 8 | Factory 8 |
| 18-21 | 0001 | Serial Number |

### B. Lookup Code Reference Tables

*See PRD.md Section 5.2 for complete lookup table structure*

### C. Glossary

| Term | Full Form | Definition |
|------|-----------|------------|
| BPAN | Battery Pack Aadhaar Number | 21-char unique battery identifier |
| BMI | Battery Manufacturer Identifier | BPAN section 1 |
| BDS | Battery Descriptor Section | BPAN section 2 |
| BI | Battery Identifier | BPAN section 3 |
| BMCS | Battery Material Composition Section | QR code data |
| BCF | Battery Carbon Footprint | QR/server data |
| BDD | Battery Dynamic Data | Server data |
| TAC | Type Allocation Code | Equipment type identifier |
| SoC | State of Charge | Battery charge level |
| FK | Foreign Key | Database reference |
| JWT | JSON Web Token | Authentication token standard |
