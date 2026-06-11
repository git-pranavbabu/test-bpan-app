# BPAN Web App - Development Changelog

## Session: 2026-05-14

---

## Features Implemented

### 1. User Authentication (No Email)
- **Removed**: Email field from User model, signup, and all related schemas
- **Fields**: Only `username` and `password` required for signup
- **Files Changed**:
  - `backend/app/models/user.py` - Removed email column
  - `backend/app/schemas/user.py` - Removed EmailStr, email field
  - `backend/app/api/v1/endpoints/auth.py` - Updated signup to not require email
  - `frontend/src/pages/Signup.jsx` - Removed email input field

### 2. Factory Code Default = 9
- **Behavior**: Factory code defaults to '9' in model creation
- **Admin Control**: Only admin can change factory code
- **Employee View**: Employees see pre-filled factory code from model (read-only)
- **Files Changed**:
  - `frontend/src/pages/AdminModels.jsx` - Factory code defaults to '9'
  - `frontend/src/pages/BPANCreate.jsx` - Employees see model.factory_code, admin can change

### 3. Employee BPAN Creation Flow
- **Admin**: Can select model + change factory code + change manufacturing date
- **Employee**: Can only select model, sees pre-filled factory code and date
- **Model Details**: Employees can only verify details (country, manufacturer, capacity, etc.)
- **Files Changed**:
  - `frontend/src/pages/BPANCreate.jsx` - Role-based UI (admin vs employee)

### 4. Last Serial Number Display
- **Endpoint**: `GET /api/v1/bpan/last-serial` returns current max serial
- **UI**: Shown in BPANCreate page header "Last Serial: X"
- **Files Changed**:
  - `backend/app/api/v1/endpoints/bpan.py` - Added /last-serial endpoint

### 5. Rejected Employees Fix
- **Issue**: Rejected employees were showing in pending tab
- **Fix**: Pending query now uses `is_approved == False AND is_active == True`
- **Files Changed**:
  - `backend/app/api/v1/endpoints/auth.py` - Updated list_pending_users

### 6. Battery Model Creation (25 Fields)
- **Order**: Fields must be filled in numbered sequence
- **Required Fields** (in order):
  1. Country Code
  2. Manufacturer Identifier
  3. Battery Capacity (kWh)
  4. Battery Chemistry
  5. Nominal Voltage
  6. Cell Origin
  7. Fire Extinguisher Class
  8. Factory Code (default 9)
  9. TAC Number
  10. Number of Cells per Battery
  11. Internal Resistance (mΩ)
  12. Battery Weight (kg)
  13. Battery Warranty (Years)
  14. Cell Type
  15. Length (mm)
  16. Width (mm)
  17. Height (mm)
  18. Type of Construction of Battery Pack
  19. Type of Construction of Module
  20. Type of Cooling System
  21. Original Power at 80% SoC (kW)
  22. Original Power at 20% SoC (kW)
  23. Total Battery Carbon Footprint (kgCO2e/kWh)
  24. Model Name

### 7. Lookup Tables - Admin Editable
- **Features**:
  - Toggle edit mode per table
  - Add new entries (code, name, description)
  - Edit existing entries inline
  - Delete entries with confirmation
- **Tables Available**:
  - countries, manufacturers, battery_capacities, battery_chemistries
  - nominal_voltages, cell_origins, extinguisher_classes, factory_codes
  - tac_numbers, cell_types, construction_types, cooling_systems

---

## Bugs Fixed (2026-05-14)

### 1. Lookup Table Add Entry Failed (Battery Capacity)
- **Issue**: Adding entries to lookup tables (e.g., battery_capacities) failed with "Failed to add entry"
- **Root Cause**: Each lookup table has different field names (e.g., `value_kwh` for battery_capacities, `name` for others)
- **Fix**: Updated `backend/app/api/v1/endpoints/lookup.py` to use table-specific field mappings:
  - `battery_capacities`: uses `value_kwh` as name field
  - `countries`: uses `name`, has `region` extra field
  - `factory_codes`: uses `factory_name`, has `location` extra field
  - etc.
- **Files Changed**: `backend/app/api/v1/endpoints/lookup.py`

### 2. Lookup Table Edit Save Not Persisting
- **Issue**: Editing an entry shows success message but changes not saved
- **Root Cause**: Update logic was only checking `name` and `description` fields generically
- **Fix**: Added specific handling for all extra fields: `region`, `country_code`, `location`
- **Files Changed**: `backend/app/api/v1/endpoints/lookup.py` - `update_entry` function

### 3. Signup Failing
- **Issue**: Signups showing "Signup failed" error
- **Root Cause**: Seed script still trying to create admin with `email` field which was removed
- **Fix**: Updated `backend/scripts/seed.py` to remove email from admin user creation
- **Files Changed**: `backend/scripts/seed.py`

### 4. Last Serial Display Padding
- **Issue**: Last serial showed as "1" instead of "0001"
- **Fix**: Added padding in `frontend/src/pages/BPANCreate.jsx`
- **Code**: `String(lastSerial).padStart(4, '0')`
- **Files Changed**: `frontend/src/pages/BPANCreate.jsx`

### 5. Quick Add (+) for Lookup Tables in Model Creation
- **Issue**: Admin needed to go to separate Lookup page to add new entries during model creation
- **Fix**: Added + button next to each dropdown in model creation form
- **Behavior**: Opens modal to add new entry to the lookup table, then refreshes the dropdown
- **Files Changed**: `frontend/src/pages/AdminModels.jsx`
- **Components Added**: `SelectWithAdd` component with inline quick-add functionality

### 6. Rejected Users Hidden from All Users List
- **Issue**: Rejected users (is_active=False) were still showing in "All Users" list
- **Fix**: Filter to show only `is_active == True` users in list_users endpoint
- **Files Changed**: `backend/app/api/v1/endpoints/auth.py` - `list_users` function

### 7. Lookup Table Name Not Displayed
- **Issue**: After adding entry to lookup table, name was not displayed (only code and description shown)
- **Root Cause**: Each table uses different field for "name" (e.g., `value_kwh` for battery_capacities, `factory_name` for factory_codes)
- **Fix**: Added `TABLE_NAME_FIELD_MAP` to map table names to their name field, and `getDisplayName()` helper function
- **Files Changed**: `frontend/src/pages/AdminLookup.jsx`

---

## Test Results

### Authentication Tests (PASSED)
1. ✅ Admin can login successfully
2. ✅ Employee can sign up
3. ✅ Employee cannot login without confirmation
4. ✅ Admin can approve employee → employee can login
5. ✅ Admin can reject from pending request → rejected employee cannot login
6. ✅ All authentication tests verified
7. ✅ All user management working

### BPAN Creation Tests
- **Create Model button** - Now working (fixed)
- **Lookup add entry** - Now working (fixed)
- **Lookup edit save** - Fixed

### Verified Working
- ✅ Delete from lookup table works
- ✅ Add entry to lookup table works (after fix)
- ✅ Edit entry in lookup table works (after fix)
- ✅ Quick add (+) button in model creation works
- ✅ Last serial shows with padding (0001 format)

---

## Architecture Notes

### Frontend Routes
```
/login          - Login page
/signup         - Signup page (no email now)
/dashboard      - User dashboard (employee/admin)
/admin          - Admin dashboard with user approval
/bpan/create    - Create BPAN (role-based: admin has extra fields)
/bpan/search     - Search BPAN by partial code
/bpan/:code     - View BPAN details, download PDF
/admin/models   - List/Deactivate/Create battery models
/admin/lookup   - View/Edit lookup tables
```

### Backend API Endpoints
```
POST /api/v1/auth/signup       - Register (username + password only)
POST /api/v1/auth/login        - Login
POST /api/v1/auth/refresh      - Refresh token
GET  /api/v1/auth/users        - List all users (admin)
GET  /api/v1/auth/users/pending - List pending users (admin)
POST /api/v1/auth/approve/:id  - Approve/Reject user (admin)

GET  /api/v1/models            - List all models (admin)
POST /api/v1/models            - Create model (admin)
DELETE /api/v1/models/:id      - Deactivate model (admin)

GET  /api/v1/lookup/tables     - List lookup tables
GET  /api/v1/lookup/:table     - List entries in table
POST /api/v1/lookup/:table     - Add entry (admin)
PUT  /api/v1/lookup/:table/:code - Update entry (admin)
DELETE /api/v1/lookup/:table/:code - Delete entry (admin)

GET  /api/v1/bpan/models-for-creation - List active models
GET  /api/v1/bpan/last-serial        - Get max serial number
POST /api/v1/bpan/generate           - Generate BPAN
GET  /api/v1/bpan/:code              - Get BPAN details
GET  /api/v1/bpan/:code/pdf          - Download PDF
POST /api/v1/bpan/decode             - Decode BPAN
POST /api/v1/bpan/qr/parse           - Parse QR code
POST /api/v1/bpan/lifecycle/update   - Update lifecycle
```

### User Roles
- **admin**: Full access, can create models, approve users, edit lookups
- **employee**: Can only create BPAN (select model + verify details)

---

## Configuration

### Environment Variables (.env)
```
DATABASE_URL=postgresql://bpan_user:bpan_password@db:5432/bpan_db
JWT_SECRET_KEY=change-me-in-production-use-at-least-32-characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@hykonindia.com
ADMIN_PASSWORD=admin_password
```

---

## Known Issues / TODO

1. ~~**Create Model button not working** - FIXED~~
2. ~~**Lookup add entry** - FIXED~~
3. ~~**Lookup edit save not persisting** - FIXED~~
4. **JWT in localStorage** - XSS vulnerability noted (not critical for internal use)
5. **No email integration** - Dashboard-only admin approval (user choice)

---

## Commands

```bash
# Start the application
cd C:\Users\mepra\Work-pranavbabu\BPAN_WEB_APP
docker-compose up --build

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1/docs
```