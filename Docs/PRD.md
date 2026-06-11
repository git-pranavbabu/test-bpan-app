# BPAN Web Application - Product Requirements Document (PRD)

**Version**: 1.0  
**Date**: May 12, 2026  
**Prepared for**: Hykon India Limited  
**Application Name**: BPAN Battery Management System

---

## 1. Executive Summary

### 1.1 Purpose

A web application for Hykon India Limited to generate and manage BPAN (Battery Pack Aadhaar Number) codes for lithium batteries. The system encodes a 21-character alphanumeric code printed on each battery pack, enabling offline identification and tracking throughout the battery lifecycle.

### 1.2 Scope

The application provides:
- **Admin Portal**: Model management, lookup table configuration, user management, reports
- **Employee Portal**: BPAN code generation with verification and PDF/HTML export
- **Authentication**: Secure JWT-based auth with email approval workflow
- **QR Code**: Deferred to Phase 2 (future requirement)

---

## 2. Product Overview

### 2.1 BPAN Concept

The BPAN (Battery Pack Aadhaar Number) serves as a unique identifier for lithium batteries, similar to Aadhaar for citizens. Each battery manufactured by Hykon India will receive a unique 21-character code that encodes manufacturing information.

### 2.2 BPAN Structure (21 Characters)

| Position | Field | Description | Example Value |
|----------|-------|-------------|---------------|
| 1-2 | Country Code | Country of manufacture | `MY` (India) |
| 3-5 | Manufacturer Identifier | Company identifier | `009` (Hykon India) |
| 6-7 | Battery Capacity | Capacity in kWh | `A6` (30 kWh) |
| 8 | Battery Chemistry | Chemistry type | `F` (NMC) |
| 9-10 | Nominal Voltage | Voltage in Volts | `KK` (307V) |
| 11-12 | Cell Origin | Country of cell origin | `KL` (Korea) |
| 13 | Extinguisher Class | Fire extinguisher class | `C` (Class C) |
| 14 | Manufacturing Year | Year (1 char) | `1` (2025) |
| 15 | Manufacturing Month | Month (1 char) | `D` (April) |
| 16 | Manufacturing Date | Date (1 char) | `H` (17th) |
| 17 | Factory Code | Factory identifier | `8` (Factory 8) |
| 18-21 | Serial Number | Unique sequential number | `0001` |

**Code Character Restriction**: The letter **`I`** is excluded from all single-character code fields (positions 8, 13, 14, 15, 16, 17) following the international standard for vehicle/battery identification codes to avoid ambiguity with the number `1`.

**Example**: `MY008 A6FKKKLC 1DH80001` decodes to:
- India / Hykon India / 30 kWh / NMC / 307V / Korea / Class C / 2025 / April / 17th / Factory 8 / Serial 0001

### 2.3 Six Categories of Battery Data

The full digital profile spans three storage locations:

**Physical BPAN (21 chars) - Categories 1-3:**
1. **BMI (Battery Manufacturer Identifier)** - Country code, Manufacturer identifier
2. **BDS (Battery Descriptor Section)** - Capacity, Chemistry, Voltage, Cell Origin, Extinguisher Class
3. **BI (Battery Identifier)** - Year, Month, Date, Factory Code, Serial Number

**QR Code Data - Categories 4-5:**
4. **BMCS (Battery Material Composition Section)** - Material composition details
5. **BCF (Battery Carbon Footprint)** - Carbon footprint data

**Server Data - Category 6:**
6. **BDD (Battery Dynamic Data)** - Real-time health and status updates

*Note: QR code functionality deferred to Phase 2*

---

## 3. User Roles and Permissions

### 3.1 Admin Account

**Creation**: First admin created via seed script (database initialization)

**Capabilities:**
| Feature | Permission |
|---------|------------|
| Lookup Tables | Create, Read, Update, Delete all entries |
| Battery Models | Create, Read, Update, Delete models |
| User Management | View all users, Approve/Reject signup requests |
| Reports | View BPAN generation statistics |
| System Configuration | Manage constant values per model |

### 3.2 Employee Account

**Creation**: Self-signup → Requires Admin approval

**Capabilities:**
| Feature | Permission |
|---------|------------|
| BPAN Generation | Select model → Verify details → Generate code |
| BPAN Retrieval | Search by 21-char code, view full details |
| Export | Download PDF, view HTML |
| Date Change Request | Request admin to modify manufacturing date |

---

## 4. Authentication Workflow

### 4.1 User Registration Flow

```
User Signup → Pending Approval → Admin Reviews → Approved/Rejected
                                           ↓
                               Approved → User can login
```

### 4.2 Login Flow

```
User Login → JWT Token Issued → Access Protected Routes
                ↓
        Token Refresh (if expired)
```

### 4.3 Admin Dashboard Approval (No Email)

- Admin reviews pending users via web dashboard
- Admin clicks "Approve" or "Reject" for each signup request
- No email integration required
- Suitable for internal company deployment

---

## 5. Database Schema

### 5.1 Core Tables

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| username | VARCHAR(50) | UNIQUE, NOT NULL |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(255) | NOT NULL |
| role | ENUM('admin', 'employee') | NOT NULL |
| is_approved | BOOLEAN | DEFAULT FALSE |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### countries
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(2) | PK |
| name | VARCHAR(100) | NOT NULL |
| region | VARCHAR(50) | NOT NULL |

#### manufacturers
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(3) | PK |
| name | VARCHAR(100) | NOT NULL |
| country_code | VARCHAR(2) | FK → countries.code |

#### battery_capacities
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(2) | PK |
| value_kwh | DECIMAL(5,2) | NOT NULL |
| description | VARCHAR(100) | |

#### battery_chemistries
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| name | VARCHAR(50) | NOT NULL |

#### nominal_voltages
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(2) | PK |
| value_v | INTEGER | NOT NULL |

#### cell_origins
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(2) | PK |
| country_name | VARCHAR(100) | NOT NULL |

#### extinguisher_classes
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| class_name | VARCHAR(50) | NOT NULL |

#### factory_codes
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| factory_name | VARCHAR(100) | NOT NULL |
| location | VARCHAR(100) | |

#### manufacturing_years
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| year | INTEGER | NOT NULL |

#### manufacturing_months
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| month_num | INTEGER | NOT NULL (1-12) |
| name | VARCHAR(20) | NOT NULL |

#### manufacturing_dates
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| day_num | INTEGER | NOT NULL (1-31) |

#### tac_numbers
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(10) | PK |
| tac_number | VARCHAR(50) | NOT NULL |

#### cell_types
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| type_name | VARCHAR(50) | NOT NULL |

#### construction_types
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(10) | PK |
| construction_type | VARCHAR(100) | NOT NULL |

#### cooling_systems
| Column | Type | Constraints |
|--------|------|-------------|
| code | VARCHAR(1) | PK |
| cooling_type | VARCHAR(50) | NOT NULL |

#### battery_models
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(100) | NOT NULL |
| country_code | VARCHAR(2) | FK → countries.code |
| manufacturer_code | VARCHAR(3) | FK → manufacturers.code |
| capacity_code | VARCHAR(2) | FK → battery_capacities.code |
| chemistry_code | VARCHAR(1) | FK → battery_chemistries.code |
| voltage_code | VARCHAR(2) | FK → nominal_voltages.code |
| cell_origin_code | VARCHAR(2) | FK → cell_origins.code |
| extinguisher_code | VARCHAR(1) | FK → extinguisher_classes.code |
| factory_code | VARCHAR(1) | FK → factory_codes.code |
| tac_code | VARCHAR(10) | FK → tac_numbers.code |
| internal_resistance | DECIMAL(6,2) | NOT NULL |
| warranty_years | INTEGER | NOT NULL |
| cell_type_code | VARCHAR(1) | FK → cell_types.code |
| pack_construction_code | VARCHAR(10) | FK → construction_types.code |
| module_construction_code | VARCHAR(10) | FK → construction_types.code |
| cooling_code | VARCHAR(1) | FK → cooling_systems.code |
| num_cells | INTEGER | NOT NULL |
| weight_kg | DECIMAL(6,2) | NOT NULL |
| length_mm | INTEGER | NOT NULL |
| width_mm | INTEGER | NOT NULL |
| height_mm | INTEGER | NOT NULL |
| power_80_soc | DECIMAL(6,2) | NOT NULL |
| power_20_soc | DECIMAL(6,2) | NOT NULL |
| carbon_footprint | DECIMAL(8,2) | NOT NULL |
| is_active | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

#### bpans
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| code_21char | VARCHAR(21) | UNIQUE, NOT NULL |
| model_id | UUID | FK → battery_models.id |
| year_code | VARCHAR(1) | FK → manufacturing_years.code |
| month_code | VARCHAR(1) | FK → manufacturing_months.code |
| date_code | VARCHAR(1) | FK → manufacturing_dates.code |
| serial_number | INTEGER | NOT NULL |
| full_data_html | TEXT | NOT NULL |
| created_by | UUID | FK → users.id |
| created_at | TIMESTAMP | NOT NULL |

#### date_change_requests
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| employee_id | UUID | FK → users.id |
| requested_date | DATE | NOT NULL |
| reason | TEXT | |
| status | ENUM('pending', 'approved', 'rejected') | DEFAULT 'pending' |
| admin_notes | TEXT | |
| created_at | TIMESTAMP | NOT NULL |
| processed_at | TIMESTAMP | |

### 5.2 Lookup Tables Summary

**Character Restriction**: The letter **`I`** is excluded from all single-character code fields (position 1 of each code for fields with 1-char codes) following the international standard for vehicle/battery identification codes to avoid ambiguity with the number `1`.

| Table | Primary Key | Description |
|-------|-------------|-------------|
| countries | code (2-char) | Country names and codes |
| manufacturers | code (3-char) | Manufacturer names |
| battery_capacities | code (2-char) | kWh values |
| battery_chemistries | code (1-char) | Chemistry types |
| nominal_voltages | code (2-char) | Voltage values |
| cell_origins | code (2-char) | Cell origin countries |
| extinguisher_classes | code (1-char) | Fire extinguisher classes |
| factory_codes | code (1-char) | Factory identifiers |
| manufacturing_years | code (1-char) | Year mapping |
| manufacturing_months | code (1-char) | Month mapping |
| manufacturing_dates | code (1-char) | Day mapping |
| tac_numbers | code | TAC numbers |
| cell_types | code (1-char) | Cell type names |
| construction_types | code | Construction type names |
| cooling_systems | code (1-char) | Cooling system types |

---

## 6. API Endpoints

### 6.1 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/auth/signup` | Public | User registration |
| POST | `/api/v1/auth/login` | Public | JWT login |
| POST | `/api/v1/auth/logout` | JWT | Invalidate token |
| POST | `/api/v1/auth/refresh` | Refresh | Refresh access token |
| POST | `/api/v1/auth/approve/{user_id}` | Admin | Approve/reject user |
| GET | `/api/v1/auth/users` | Admin | List all users |
| GET | `/api/v1/auth/users/pending` | Admin | List pending approvals |

### 6.2 Lookup Tables

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/lookup/{table}` | Admin | List all entries |
| POST | `/api/v1/lookup/{table}` | Admin | Create entry |
| GET | `/api/v1/lookup/{table}/{code}` | Admin | Get single entry |
| PUT | `/api/v1/lookup/{table}/{code}` | Admin | Update entry |
| DELETE | `/api/v1/lookup/{table}/{code}` | Admin | Delete entry |
| POST | `/api/v1/lookup/{table}/import` | Admin | Bulk import CSV |
| GET | `/api/v1/lookup/tables` | Admin | List all table names |

### 6.3 Battery Models

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/models` | Admin | List all models |
| POST | `/api/v1/models` | Admin | Create model |
| GET | `/api/v1/models/{id}` | Admin | Get model details |
| PUT | `/api/v1/models/{id}` | Admin | Update model |
| DELETE | `/api/v1/models/{id}` | Admin | Deactivate model |
| GET | `/api/v1/models/active` | Employee | List active models |

### 6.4 BPAN Generation

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/bpan/models-for-creation` | Employee | Get models for BPAN creation |
| POST | `/api/v1/bpan/generate` | Employee | Generate new BPAN |
| GET | `/api/v1/bpan/{code}` | Employee | Get BPAN details |
| GET | `/api/v1/bpan/{code}/pdf` | Employee | Download PDF |
| GET | `/api/v1/bpan/{code}/html` | Employee | Get HTML view |
| GET | `/api/v1/bpan/search` | Employee | Search BPAN by code |

### 6.5 Reports

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/reports/today` | Admin | BPANs created today |
| GET | `/api/v1/reports/week` | Admin | BPANs created this week |
| GET | `/api/v1/reports/month` | Admin | BPANs created this month |
| GET | `/api/v1/reports/history` | Admin | All BPANs with pagination |

### 6.6 Date Change Requests

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/date-requests` | Employee | Submit date change request |
| GET | `/api/v1/date-requests` | Admin | List pending requests |
| POST | `/api/v1/date-requests/{id}/approve` | Admin | Approve request |
| POST | `/api/v1/date-requests/{id}/reject` | Admin | Reject request |

---

## 7. BPAN Generation Process

### 7.1 Employee Workflow

```
1. Employee logs in
2. Clicks "Create New BPAN"
3. System displays:
   - Current manufacturing date (auto-filled from server)
   - Auto-generated serial number (increments per day/factory)
   - Available battery models (dropdown)
4. Employee selects model
5. Employee verifies:
   - Manufacturing date
   - Serial number
   - Selected model
6. Employee clicks "Generate"
7. System:
   - Assembles 21-char code from model constants + date + serial
   - Stores in database
   - Returns success with code
8. Employee can:
   - View details
   - Download PDF
   - View HTML
```

### 7.2 Code Assembly Logic

```
BPAN = CountryCode(2) + ManufacturerCode(3) + CapacityCode(2) + ChemistryCode(1) 
     + VoltageCode(2) + CellOriginCode(2) + ExtinguisherCode(1) 
     + YearCode(1) + MonthCode(1) + DateCode(1) + FactoryCode(1) 
     + SerialNumber(4, zero-padded)
```

### 7.3 Serial Number Logic

- Auto-increments globally across all products (not per model or day)
- Format: 4-digit zero-padded (0001, 0002, ...)
- Unique across entire system

---

## 8. PDF Generation

### 8.1 PDF Content

The generated PDF includes:
- BPAN 21-character code (large, scannable format)
- Full decoded information:
  - Country and Manufacturer
  - Battery specifications (capacity, chemistry, voltage)
  - Manufacturing details (date, factory, serial)
  - Model-specific constant values
- QR code placeholder (Phase 2)
- Generation timestamp

### 8.2 PDF Design

- **Phase 1**: Generic layout with company-neutral styling
- **Phase 2+**: Hykon India branding integration

---

## 9. Security Requirements

### 9.1 Authentication Security

| Measure | Implementation |
|---------|----------------|
| Password Hashing | argon2 with salt |
| Token Type | JWT (RS256) |
| Access Token Expiry | 30 minutes |
| Refresh Token Expiry | 7 days |
| Password Minimum | 8 characters |

### 9.2 API Security

| Measure | Implementation |
|---------|----------------|
| SQL Injection | SQLAlchemy ORM with parameterized queries |
| Input Validation | Pydantic schemas for all inputs |
| Rate Limiting | 5 failed login attempts → 15 min lockout |
| CORS | Strict origin validation |
| HTTPS | Required in production |

### 9.3 Audit Logging

All actions logged:
- User login/logout
- BPAN generation
- Lookup table changes
- User approval/rejection
- Model creation/modification

---

## 10. Technical Architecture

### 10.1 Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React + Tailwind CSS |
| Backend | Python/FastAPI |
| Database | PostgreSQL |
| Auth | JWT (PyJWT + python-jose) |
| PDF Generation | ReportLab |
| Password Hashing | argon2-cffi |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Container | Docker + Docker Compose |

### 10.2 Project Structure

```
bpan_web_app/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── requirements.txt
│   └── alembic/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── App.jsx
│   └── package.json
├── docker-compose.yml
└── docs/
    ├── PRD.md
    └── SRS.md
```

---

## 11. Implementation Phases

| Phase | Description |
|-------|-------------|
| **Phase 0** | Project scaffold, Docker Compose, folder structure, seed admin user |
| **Phase 1** | Database models, migrations, environment configuration |
| **Phase 2** | Auth endpoints (signup → approval → login → JWT), audit logging |
| **Phase 3** | Lookup tables CRUD, bulk CSV import |
| **Phase 4** | Battery models CRUD |
| **Phase 5** | BPAN generation, serial number auto-increment |
| **Phase 6** | PDF/HTML generation |
| **Phase 7** | Reports dashboard |
| **Phase 8** | React frontend SPA |
| **Phase 9** | Testing, bug fixes, refinement |

---

## 12. Deferred Requirements

| Feature | Phase |
|---------|-------|
| QR Code generation | Phase 2 |
| Hykon India branding | Phase 2+ |
| Mobile responsiveness | Phase 2+ |
| Bulk BPAN generation | Phase 2+ |
| Battery lifecycle tracking | Phase 2+ |

---

## 13. Seed Data Requirements

For initial setup, the following must be provided:

1. **First Admin User**
   - Username
   - Email
   - Password (temporary, to be changed on first login)

2. **Initial Country**
   - Country Code: `MY`
   - Country Name: `India`
   - Region: `Asia`

3. **Manufacturer**
   - Code: `009`
   - Name: `Hykon India Limited`
   - Country: `MY` (India)

4. **Factory**
   - Code: `1`
   - Factory Name: `Hykon India Factory 1`
   - Location: `India`

---

## 14. Glossary

| Term | Definition |
|------|------------|
| BPAN | Battery Pack Aadhaar Number - 21-char unique identifier |
| BMI | Battery Manufacturer Identifier - Country + Manufacturer |
| BDS | Battery Descriptor Section - Capacity, Chemistry, Voltage, Cell Origin, Extinguisher |
| BI | Battery Identifier - Date, Factory, Serial |
| BMCS | Battery Material Composition Section (QR data) |
| BCF | Battery Carbon Footprint (QR/Server data) |
| BDD | Battery Dynamic Data (Server data) |
| TAC | Type Allocation Code |
| SoC | State of Charge |
