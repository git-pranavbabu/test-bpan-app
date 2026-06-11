"""
Seed script to create initial admin user and base lookup table data.
Run with: python -m scripts.seed
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole
from app.models.battery_model import BatteryModel
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
    NumberOfCells,
    Dimensions,
    Power80Soc,
    Power20Soc,
    CarbonFootprint,
)


def seed_admin_user(db: Session) -> None:
    existing_admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
    if existing_admin:
        print(f"Admin user '{settings.ADMIN_USERNAME}' already exists. Skipping...")
        return
    
    admin = User(
        username=settings.ADMIN_USERNAME,
        password_hash=get_password_hash(settings.ADMIN_PASSWORD),
        role=UserRole.admin,
        is_approved=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    print(f"Created admin user: {settings.ADMIN_USERNAME}")


def seed_initial_countries(db: Session) -> None:
    pass


def seed_initial_manufacturers(db: Session) -> None:
    pass


def seed_initial_factory(db: Session) -> None:
    if db.query(FactoryCode).filter(FactoryCode.code == "9").first():
        print("Factory code '9' already exists. Skipping...")
        return
    
    factory = FactoryCode(
        code="9",
        factory_name="9",
        location="India",
    )
    db.add(factory)
    db.commit()
    print("Seeded factory code '9'")


def seed_date_codes(db: Session) -> None:
    existing_years = db.query(ManufacturingYear).count()
    if existing_years > 0:
        print("Year codes already exist. Skipping...")
    else:
        year_codes = [
            ManufacturingYear(code="1", year=2025),
            ManufacturingYear(code="2", year=2026),
            ManufacturingYear(code="3", year=2027),
            ManufacturingYear(code="4", year=2028),
            ManufacturingYear(code="5", year=2029),
            ManufacturingYear(code="6", year=2030),
            ManufacturingYear(code="7", year=2031),
            ManufacturingYear(code="8", year=2032),
            ManufacturingYear(code="9", year=2033),
        ]
        for y in year_codes:
            db.add(y)
        db.commit()
        print("Seeded year codes 1-9 (2025-2033)")
    
    existing_months = db.query(ManufacturingMonth).count()
    if existing_months > 0:
        print("Month codes already exist. Skipping...")
    else:
        month_codes = [
            ManufacturingMonth(code="A", month_num=1, name="January"),
            ManufacturingMonth(code="B", month_num=2, name="February"),
            ManufacturingMonth(code="C", month_num=3, name="March"),
            ManufacturingMonth(code="D", month_num=4, name="April"),
            ManufacturingMonth(code="E", month_num=5, name="May"),
            ManufacturingMonth(code="F", month_num=6, name="June"),
            ManufacturingMonth(code="G", month_num=7, name="July"),
            ManufacturingMonth(code="H", month_num=8, name="August"),
            ManufacturingMonth(code="J", month_num=9, name="September"),
            ManufacturingMonth(code="K", month_num=10, name="October"),
            ManufacturingMonth(code="L", month_num=11, name="November"),
            ManufacturingMonth(code="M", month_num=12, name="December"),
        ]
        for m in month_codes:
            db.add(m)
        db.commit()
        print("Seeded month codes A-M (Jan-Dec, excluding I)")
    
    existing_dates = db.query(ManufacturingDate).count()
    if existing_dates > 0:
        print("Date codes already exist. Skipping...")
    else:
        date_codes = [
            ManufacturingDate(code="1", day_num=1),
            ManufacturingDate(code="2", day_num=2),
            ManufacturingDate(code="3", day_num=3),
            ManufacturingDate(code="4", day_num=4),
            ManufacturingDate(code="5", day_num=5),
            ManufacturingDate(code="6", day_num=6),
            ManufacturingDate(code="7", day_num=7),
            ManufacturingDate(code="8", day_num=8),
            ManufacturingDate(code="9", day_num=9),
            ManufacturingDate(code="A", day_num=10),
            ManufacturingDate(code="B", day_num=11),
            ManufacturingDate(code="C", day_num=12),
            ManufacturingDate(code="D", day_num=13),
            ManufacturingDate(code="E", day_num=14),
            ManufacturingDate(code="F", day_num=15),
            ManufacturingDate(code="G", day_num=16),
            ManufacturingDate(code="H", day_num=17),
            ManufacturingDate(code="J", day_num=18),
            ManufacturingDate(code="K", day_num=19),
            ManufacturingDate(code="L", day_num=20),
            ManufacturingDate(code="M", day_num=21),
            ManufacturingDate(code="N", day_num=22),
            ManufacturingDate(code="P", day_num=23),
            ManufacturingDate(code="R", day_num=24),
            ManufacturingDate(code="S", day_num=25),
            ManufacturingDate(code="T", day_num=26),
            ManufacturingDate(code="U", day_num=27),
            ManufacturingDate(code="V", day_num=28),
        ]
        for d in date_codes:
            db.add(d)
        db.commit()
        print("Seeded date codes 1-9, A-V (days 1-27, excluding I)")


def _add_if_not_exists(db, model, filter_kwargs, create_kwargs, label):
    existing = db.query(model).filter_by(**filter_kwargs).first()
    if existing:
        print(f"  {label}: already exists. Skipping...")
        return existing
    entry = model(**create_kwargs)
    db.add(entry)
    db.flush()
    print(f"  Created {label}")
    return entry


def seed_models(db: Session) -> None:
    models_to_seed = [
        {"name": "HiLIFE 12.8", "capacity": ("AA", 1.28), "voltage": ("AM", 12.8), "num_cells": ("4", 4),
         "weight": ("AM", 12), "dims": ("D160x146x450", 160, 146, 450), "p80": ("AA", 0.99), "p20": (0.24, None),
         "carbon": ("96", 96), "tac": "AP0001"},
        {"name": "HiLIFE 25.6", "capacity": ("AB", 2.56), "voltage": ("A1", 25.6), "num_cells": ("8", 8),
         "weight": ("AY", 23), "dims": ("D270x146x450", 270, 146, 450), "p80": ("AB", 2.0), "p20": (0.5, None),
         "carbon": ("200", 200), "tac": "AP0002"},
        {"name": "HiLIFE 35.6", "capacity": ("AC", 3.5), "voltage": ("BB", 35.2), "num_cells": ("11", 11),
         "weight": ("A5", 29), "dims": ("D350x146x450", 350, 146, 450), "p80": ("AB", 2.8), "p20": (0.7, None),
         "carbon": ("280", 280), "tac": "AP0003"},
        {"name": "HiLIFE 48", "capacity": ("AD", 4.8), "voltage": ("BQ", 48), "num_cells": ("15", 15),
         "weight": ("BF", 39), "dims": ("D465x146x450", 465, 146, 450), "p80": ("AC", 3.8), "p20": (0.9, "AA"),
         "carbon": ("384", 384), "tac": "AP0004"},
        {"name": "HiLIFE 51.2", "capacity": ("AE", 5.12), "voltage": ("BT", 51.2), "num_cells": ("16", 16),
         "weight": ("BK", 43), "dims": ("D465x146x450", 465, 146, 450), "p80": ("AD", 4.0), "p20": (1.0, "AA"),
         "carbon": ("409", 409), "tac": "AP0005"},
        {"name": "HiLIFE 73.6", "capacity": ("AG", 7.3), "voltage": ("CG", 73.6), "num_cells": ("23", 23),
         "weight": ("B4", 61), "dims": ("D400x316x475", 400, 316, 475), "p80": ("AE", 5.8), "p20": (1.46, "AA"),
         "carbon": ("584", 584), "tac": "AP0006"},
        {"name": "HiLIFE 96", "capacity": ("AJ", 9.6), "voltage": ("C6", 96), "num_cells": ("30", 30),
         "weight": ("CL", 77), "dims": ("D480x316x475", 480, 316, 475), "p80": ("AG", 7.6), "p20": (1.9, "AB"),
         "carbon": ("768", 768), "tac": "AP0007"},
        {"name": "HiLIFE 121.6", "capacity": ("AM", 12.16), "voltage": ("DX", 121.6), "num_cells": ("38", 38),
         "weight": ("C6", 96), "dims": ("D590x316x475", 590, 316, 475), "p80": ("AJ", 9.6), "p20": (2.4, "AB"),
         "carbon": ("968", 968), "tac": "AP0008"},
        {"name": "HLH 5.12", "capacity": ("AE", 5.12), "voltage": ("BT", 51.2), "num_cells": ("16", 16),
         "weight": ("BK", 43), "dims": ("D500x520x138", 500, 520, 138), "p80": ("AD", 4.0), "p20": (1.0, "AA"),
         "carbon": ("409", 409), "tac": "AP0009"},
        {"name": "HLH 10.24", "capacity": ("AK", 10.24), "voltage": ("BT", 51.2), "num_cells": ("16", 16),
         "weight": ("CV", 86), "dims": ("D885x520x138", 885, 520, 138), "p80": ("AH", 8.0), "p20": (2.0, "AB"),
         "carbon": ("819", 819), "tac": "AP0010"},
    ]

    print("Seeding shared lookup entries...")
    _add_if_not_exists(db, Country, {"code": "MD"}, {"code": "MD", "name": "India", "region": "Asia"}, "Country MD")
    _add_if_not_exists(db, Manufacturer, {"code": "009"}, {"code": "009", "name": "Hykon India Limited", "country_code": "MD"}, "Manufacturer 009")
    _add_if_not_exists(db, BatteryChemistry, {"code": "E"}, {"code": "E", "name": "LFP"}, "BatteryChemistry E (LFP)")
    _add_if_not_exists(db, CellOrigin, {"code": "L"}, {"code": "L", "country_name": "China"}, "CellOrigin L (China)")
    _add_if_not_exists(db, ExtinguisherClass, {"code": "D"}, {"code": "D", "class_code": "D", "class_name": "D"}, "ExtinguisherClass D")
    _add_if_not_exists(db, FactoryCode, {"code": "9"}, {"code": "9", "factory_name": "9", "location": "India"}, "FactoryCode 9")
    _add_if_not_exists(db, CellType, {"code": "B"}, {"code": "B", "type_name": "Prismatic"}, "CellType B")
    _add_if_not_exists(db, PackConstructionType, {"code": "A"}, {"code": "A", "construction_type": "Cell-to-Module-to-Pack (CTMTP)"}, "PackConstructionType A")
    _add_if_not_exists(db, ModuleConstructionType, {"code": "A"}, {"code": "A", "construction_type": "Series"}, "ModuleConstructionType A")
    _add_if_not_exists(db, CoolingSystem, {"code": "A"}, {"code": "A", "cooling_type": "Air"}, "CoolingSystem A")
    _add_if_not_exists(db, InternalResistance, {"code": "175"}, {"code": "175", "value_mohm": 175}, "InternalResistance 175")
    _add_if_not_exists(db, BatteryWarranty, {"code": "E"}, {"code": "E", "years": 5}, "BatteryWarranty E")

    from collections import OrderedDict
    seen = OrderedDict()

    for m in models_to_seed:
        c_code, c_val = m["capacity"]
        seen.setdefault(("capacity", c_code), (BatteryCapacity, {"code": c_code, "value_kwh": c_val}, f"BatteryCapacity {c_code} ({c_val} kWh)"))
        v_code, v_val = m["voltage"]
        seen.setdefault(("voltage", v_code), (NominalVoltage, {"code": v_code, "value_v": v_val}, f"NominalVoltage {v_code} ({v_val}V)"))
        n_code, n_val = m["num_cells"]
        seen.setdefault(("num_cells", n_code), (NumberOfCells, {"code": n_code, "count": n_val}, f"NumberOfCells {n_code}"))
        w_code, w_val = m["weight"]
        seen.setdefault(("weight", w_code), (BatteryWeight, {"code": w_code, "value_kg": w_val}, f"BatteryWeight {w_code} ({w_val} kg)"))
        d_code, d_l, d_w, d_h = m["dims"]
        seen.setdefault(("dims", d_code), (Dimensions, {"code": d_code, "length_mm": d_l, "width_mm": d_w, "height_mm": d_h}, f"Dimensions {d_code}"))
        p80_code, p80_val = m["p80"]
        seen.setdefault(("p80", p80_code), (Power80Soc, {"code": p80_code, "value_kw": p80_val}, f"Power80Soc {p80_code} ({p80_val} kW)"))
        p20_val, p20_code = m["p20"]
        seen.setdefault(("p20", str(p20_val)), (Power20Soc, {"value_kw": p20_val, "code": p20_code}, f"Power20Soc {p20_val} kW"))
        c_code, c_val = m["carbon"]
        seen.setdefault(("carbon", c_code), (CarbonFootprint, {"code": c_code, "value_kgco2ekwh": c_val}, f"CarbonFootprint {c_code}"))
        t_code = m["tac"]
        seen.setdefault(("tac", t_code), (TACNumber, {"code": t_code, "tac_number": t_code}, f"TACNumber {t_code}"))

    for (kind, code), (model_cls, kwargs, label) in seen.items():
        _add_if_not_exists(db, model_cls, {"code": code} if kind != "p20" else {"value_kw": kwargs["value_kw"]}, kwargs, label)

    db.commit()

    for m in models_to_seed:
        name = m["name"]
        if db.query(BatteryModel).filter(BatteryModel.name == name).first():
            print(f"Model '{name}' already exists. Skipping...")
            continue

        print(f"Creating model '{name}'...")
        model = BatteryModel(
            name=name,
            country_code="MD", manufacturer_code="009",
            capacity_code=m["capacity"][0], chemistry_code="E",
            voltage_code=m["voltage"][0], cell_origin_code="L",
            extinguisher_code="D", factory_code="9",
            tac_code=m["tac"],
            internal_resistance_code="175", warranty_code="E",
            cell_type_code="B",
            pack_construction_code="A", module_construction_code="A",
            cooling_code="A",
            num_cells_code=m["num_cells"][0],
            weight_code=m["weight"][0],
            dimensions_code=m["dims"][0],
            power_80_soc_code=m["p80"][0],
            power_20_soc_value=m["p20"][0],
            carbon_footprint_code=m["carbon"][0],
        )
        db.add(model)
        db.commit()
        print(f"  Created {name}")


def run_seed() -> None:
    print("Starting database seed...")
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_initial_countries(db)
        seed_initial_manufacturers(db)
        seed_initial_factory(db)
        seed_date_codes(db)
        seed_models(db)
        print("Database seed completed successfully!")
    except Exception as e:
        print(f"Error during seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
