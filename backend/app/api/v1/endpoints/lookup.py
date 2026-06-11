from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.models.user import User
from app.models.lookup import (
    Country,
    Manufacturer,
    BatteryCapacity,
    BatteryChemistry,
    NominalVoltage,
    CellOrigin,
    ExtinguisherClass,
    FactoryCode,
    ManufacturingYear,
    ManufacturingMonth,
    ManufacturingDate,
    TACNumber,
    CellType,
    PackConstructionType,
    ModuleConstructionType,
    CoolingSystem,
    InternalResistance,
    BatteryWeight,
    BatteryWarranty,
    Power80Soc,
    Power20Soc,
    CarbonFootprint,
    NumberOfCells,
    Dimensions,
)
from app.api.v1.endpoints.auth import get_current_user, require_admin

router = APIRouter()

TABLE_CODE_MAX_LENGTH = {
    "countries": 2,
    "manufacturers": 3,
    "battery_capacities": 2,
    "battery_chemistries": 1,
    "nominal_voltages": 2,
    "cell_origins": 2,
    "extinguisher_classes": 1,
    "factory_codes": 1,
    "manufacturing_years": 1,
    "manufacturing_months": 1,
    "manufacturing_dates": 1,
    "tac_numbers": 10,
    "cell_types": 1,
    "pack_construction_types": 10,
    "module_construction_types": 10,
    "cooling_systems": 1,
    "internal_resistances": 10,
    "battery_weights": 10,
    "battery_warranties": 10,
    "power_80_soc": 10,
    "power_20_soc": 10,
    "carbon_footprints": 10,
    "number_of_cells": 10,
    "dimensions": 20,
}

LOOKUP_TABLES = {
    "countries": {"model": Country, "description": "Country codes and names", "name_field": "name", "extra_fields": {"region": str}},
    "manufacturers": {"model": Manufacturer, "description": "Manufacturer identifiers", "name_field": "name", "extra_fields": {"country_code": str}},
    "battery_capacities": {"model": BatteryCapacity, "description": "Battery capacity in kWh", "name_field": "value_kwh", "extra_fields": {"description": str}},
    "battery_chemistries": {"model": BatteryChemistry, "description": "Chemistry type codes", "name_field": "name", "extra_fields": {}},
    "nominal_voltages": {"model": NominalVoltage, "description": "Voltage values", "name_field": "value_v", "extra_fields": {}},
    "cell_origins": {"model": CellOrigin, "description": "Cell origin countries", "name_field": "country_name", "extra_fields": {}},
    "extinguisher_classes": {"model": ExtinguisherClass, "description": "Fire extinguisher classes", "name_field": "class_name", "extra_fields": {"class_code": str}},
    "factory_codes": {"model": FactoryCode, "description": "Factory identifiers", "name_field": "factory_name", "extra_fields": {"location": str}},
    "manufacturing_years": {"model": ManufacturingYear, "description": "Year code mapping", "name_field": "year", "extra_fields": {}},
    "manufacturing_months": {"model": ManufacturingMonth, "description": "Month code mapping", "name_field": "name", "extra_fields": {"month_num": int}},
    "manufacturing_dates": {"model": ManufacturingDate, "description": "Date code mapping", "name_field": "day_num", "extra_fields": {}},
    "tac_numbers": {"model": TACNumber, "description": "TAC number codes", "name_field": "tac_number", "extra_fields": {}},
    "cell_types": {"model": CellType, "description": "Cell type names", "name_field": "type_name", "extra_fields": {}},
    "pack_construction_types": {"model": PackConstructionType, "description": "Pack construction types", "name_field": "construction_type", "extra_fields": {}},
    "module_construction_types": {"model": ModuleConstructionType, "description": "Module construction types", "name_field": "construction_type", "extra_fields": {}},
    "cooling_systems": {"model": CoolingSystem, "description": "Cooling system types", "name_field": "cooling_type", "extra_fields": {}},
    "internal_resistances": {"model": InternalResistance, "description": "Internal resistance in mΩ", "name_field": "value_mohm", "extra_fields": {"description": str}},
    "battery_weights": {"model": BatteryWeight, "description": "Battery weight in kg", "name_field": "value_kg", "extra_fields": {"description": str}},
    "battery_warranties": {"model": BatteryWarranty, "description": "Battery warranty in years", "name_field": "years", "extra_fields": {"description": str}},
    "power_80_soc": {"model": Power80Soc, "description": "Power at 80% SoC in kW", "name_field": "value_kw", "extra_fields": {"description": str}},
    "power_20_soc": {"model": Power20Soc, "description": "Power at 20% SoC in kW", "name_field": "value_kw", "extra_fields": {"description": str}},
    "carbon_footprints": {"model": CarbonFootprint, "description": "Carbon footprint in kgCO2e/kWh", "name_field": "value_kgco2ekwh", "extra_fields": {"description": str}},
    "number_of_cells": {"model": NumberOfCells, "description": "Number of cells per battery", "name_field": "count", "extra_fields": {"description": str}},
    "dimensions": {"model": Dimensions, "description": "Dimensions in mm (L×W×H)", "name_field": "dimensions", "extra_fields": {}},
}

TABLE_NAME_FIELD_MAP = {name: info["name_field"] for name, info in LOOKUP_TABLES.items()}


def get_table_model(table_name: str):
    if table_name not in LOOKUP_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    return LOOKUP_TABLES[table_name]["model"]


@router.get("/tables")
def list_tables(current_user: User = Depends(get_current_user)):
    return [
        {
            "name": name, 
            "description": info["description"],
            "extra_fields": list(info.get("extra_fields", {}).keys())
        }
        for name, info in LOOKUP_TABLES.items()
    ]


@router.get("/{table}")
def list_entries(table: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    model = get_table_model(table)
    entries = db.query(model).all()
    return entries


@router.post("/{table}")
def create_entry(table: str, entry_data: dict, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if table not in LOOKUP_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
    
    model = LOOKUP_TABLES[table]["model"]
    info = LOOKUP_TABLES[table]
    name_field = info["name_field"]
    
    try:
        if table == "power_20_soc":
            value_kw = float(entry_data.get("name", entry_data.get("value_kw", 0)))
            if value_kw <= 0:
                raise HTTPException(status_code=400, detail="Power value must be greater than 0")
            
            existing = db.query(model).filter(model.value_kw == value_kw).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Entry with value {value_kw} kW already exists")
            
            create_data = {
                "value_kw": value_kw,
                "code": entry_data.get("code") or None,
                "description": entry_data.get("description", "")
            }
            entry = model(**create_data)
            db.add(entry)
            db.commit()
            return {"message": f"Entry {value_kw} kW created successfully", "value_kw": value_kw}
        
        code = entry_data.get("code", "")
        if not code:
            raise HTTPException(status_code=400, detail="Code is required")
        
        if table in TABLE_CODE_MAX_LENGTH:
            max_len = TABLE_CODE_MAX_LENGTH[table]
            if len(code) > max_len:
                raise HTTPException(
                    status_code=400,
                    detail=f"Code '{code}' is too long. Maximum length for {table} is {max_len} character(s)."
                )
        
        existing = db.query(model).filter(model.code == code).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"Entry with code '{code}' already exists")
        
        create_data = {"code": str(code).strip()}
        
        if table == "dimensions":
            if "length_mm" not in entry_data or "width_mm" not in entry_data or "height_mm" not in entry_data:
                raise HTTPException(status_code=400, detail="length_mm, width_mm, and height_mm are required for dimensions")
            try:
                create_data["length_mm"] = int(entry_data["length_mm"])
                create_data["width_mm"] = int(entry_data["width_mm"])
                create_data["height_mm"] = int(entry_data["height_mm"])
            except ValueError:
                raise HTTPException(status_code=400, detail="Dimensions must be valid integers")
        else:
            name_value = entry_data.get("name")
            if name_value is None and not code:
                raise HTTPException(status_code=400, detail=f"A value for {name_field} is required")
            if name_value is None:
                name_value = code
                
            if name_field in ["value_kwh", "value_v", "value_mohm", "value_kg", "value_kw", "value_kgco2ekwh"]:
                try:
                    name_value = float(name_value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid numeric value for {name_field}: '{name_value}'")
            elif name_field in ["year", "day_num", "years", "count"]:
                try:
                    name_value = int(name_value)
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid integer value for {name_field}: '{name_value}'")
            create_data[name_field] = name_value
        
        for extra_field, field_type in info.get("extra_fields", {}).items():
            if extra_field in ["class_code", "country_code", "month_num"]:
                if extra_field not in entry_data or not str(entry_data[extra_field]).strip():
                    raise HTTPException(status_code=400, detail=f"{extra_field} is required")
            if extra_field in entry_data and str(entry_data[extra_field]).strip():
                try:
                    create_data[extra_field] = field_type(entry_data[extra_field])
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid type for {extra_field}")
        
        entry = model(**create_data)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.put("/{table}/{identifier}")
def update_entry(table: str, identifier: str, entry_data: dict, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    if table not in LOOKUP_TABLES:
        raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
    
    model = LOOKUP_TABLES[table]["model"]
    name_field = LOOKUP_TABLES[table]["name_field"]
    
    if table == "power_20_soc":
        try:
            entry_id = int(identifier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid identifier: must be an integer for power_20_soc")
        entry = db.query(model).filter(model.id == entry_id).first()
    else:
        entry = db.query(model).filter(model.code == identifier).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{identifier}' not found")
    
    if table == "dimensions":
        if "length_mm" in entry_data:
            entry.length_mm = int(entry_data["length_mm"])
        if "width_mm" in entry_data:
            entry.width_mm = int(entry_data["width_mm"])
        if "height_mm" in entry_data:
            entry.height_mm = int(entry_data["height_mm"])
    elif "name" in entry_data:
        name_value = entry_data["name"]
        if name_field in ["value_kwh", "value_v", "value_kw", "value_mohm", "value_kg", "value_kgco2ekwh"]:
            try:
                name_value = float(name_value)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Invalid value for {name_field}")
        elif name_field in ["year", "day_num", "years", "count"]:
            try:
                name_value = int(name_value)
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail=f"Invalid value for {name_field}")
        setattr(entry, name_field, name_value)
    for extra_field, field_type in LOOKUP_TABLES[table].get("extra_fields", {}).items():
        if extra_field in entry_data and hasattr(entry, extra_field):
            if str(entry_data[extra_field]).strip():
                try:
                    setattr(entry, extra_field, field_type(entry_data[extra_field]))
                except (ValueError, TypeError):
                    raise HTTPException(status_code=400, detail=f"Invalid type for {extra_field}")
            elif extra_field not in ["class_code", "country_code", "month_num"]:
                setattr(entry, extra_field, None)
    
    try:
        db.commit()
        db.refresh(entry)
        return entry
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e.orig)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.delete("/{table}/{identifier}")
def delete_entry(table: str, identifier: str, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    model = get_table_model(table)
    
    if table == "power_20_soc":
        try:
            entry_id = int(identifier)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid identifier: must be an integer for power_20_soc")
        entry = db.query(model).filter(model.id == entry_id).first()
    else:
        entry = db.query(model).filter(model.code == identifier).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail=f"Entry '{identifier}' not found")
    
    db.delete(entry)
    db.commit()
    return {"message": f"Entry '{identifier}' deleted successfully"}
