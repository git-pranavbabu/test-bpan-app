from app.core.database import Base
from sqlalchemy import Column, String, Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone


class Country(Base):
    __tablename__ = "countries"

    code = Column(String(2), primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    manufacturers = relationship("Manufacturer", back_populates="country")


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    code = Column(String(3), primary_key=True)
    name = Column(String(100), nullable=False)
    country_code = Column(String(2), ForeignKey("countries.code"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    country = relationship("Country", back_populates="manufacturers")


class BatteryCapacity(Base):
    __tablename__ = "battery_capacities"

    code = Column(String(2), primary_key=True)
    value_kwh = Column(Numeric(5, 2), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BatteryChemistry(Base):
    __tablename__ = "battery_chemistries"

    code = Column(String(1), primary_key=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NominalVoltage(Base):
    __tablename__ = "nominal_voltages"

    code = Column(String(2), primary_key=True)
    value_v = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CellOrigin(Base):
    __tablename__ = "cell_origins"

    code = Column(String(2), primary_key=True)
    country_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ExtinguisherClass(Base):
    __tablename__ = "extinguisher_classes"

    code = Column(String(1), primary_key=True)
    class_code = Column(String(10), nullable=False)
    class_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FactoryCode(Base):
    __tablename__ = "factory_codes"

    code = Column(String(1), primary_key=True)
    factory_name = Column(String(100), nullable=False)
    location = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ManufacturingYear(Base):
    __tablename__ = "manufacturing_years"

    code = Column(String(1), primary_key=True)
    year = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ManufacturingMonth(Base):
    __tablename__ = "manufacturing_months"

    code = Column(String(1), primary_key=True)
    month_num = Column(Integer, nullable=False)
    name = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ManufacturingDate(Base):
    __tablename__ = "manufacturing_dates"

    code = Column(String(1), primary_key=True)
    day_num = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class TACNumber(Base):
    __tablename__ = "tac_numbers"

    code = Column(String(10), primary_key=True)
    tac_number = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CellType(Base):
    __tablename__ = "cell_types"

    code = Column(String(1), primary_key=True)
    type_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class PackConstructionType(Base):
    __tablename__ = "pack_construction_types"

    code = Column(String(10), primary_key=True)
    construction_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ModuleConstructionType(Base):
    __tablename__ = "module_construction_types"

    code = Column(String(10), primary_key=True)
    construction_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CoolingSystem(Base):
    __tablename__ = "cooling_systems"

    code = Column(String(1), primary_key=True)
    cooling_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class InternalResistance(Base):
    __tablename__ = "internal_resistances"

    code = Column(String(10), primary_key=True)
    value_mohm = Column(Numeric(6, 2), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BatteryWeight(Base):
    __tablename__ = "battery_weights"

    code = Column(String(10), primary_key=True)
    value_kg = Column(Numeric(6, 2), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class BatteryWarranty(Base):
    __tablename__ = "battery_warranties"

    code = Column(String(10), primary_key=True)
    years = Column(Integer, nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Power80Soc(Base):
    __tablename__ = "power_80_soc"

    code = Column(String(10), primary_key=True)
    value_kw = Column(Numeric(6, 2), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Power20Soc(Base):
    __tablename__ = "power_20_soc"

    id = Column(Integer, primary_key=True, autoincrement=True)
    value_kw = Column(Numeric(6, 2), nullable=False, unique=True)
    code = Column(String(10), nullable=True)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"

    code = Column(String(10), primary_key=True)
    value_kgco2ekwh = Column(Numeric(8, 2), nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class NumberOfCells(Base):
    __tablename__ = "number_of_cells"

    code = Column(String(10), primary_key=True)
    count = Column(Integer, nullable=False)
    description = Column(String(100))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Dimensions(Base):
    __tablename__ = "dimensions"

    code = Column(String(20), primary_key=True)
    length_mm = Column(Integer, nullable=False)
    width_mm = Column(Integer, nullable=False)
    height_mm = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
