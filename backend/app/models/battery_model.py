from app.core.database import Base
from sqlalchemy import Column, String, Numeric, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, foreign, remote
import uuid
from datetime import datetime, timezone


class BatteryModel(Base):
    __tablename__ = "battery_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, index=True)
    
    country_code = Column(String(2), ForeignKey("countries.code"), nullable=False)
    manufacturer_code = Column(String(3), ForeignKey("manufacturers.code"), nullable=False)
    capacity_code = Column(String(2), ForeignKey("battery_capacities.code"), nullable=False)
    chemistry_code = Column(String(1), ForeignKey("battery_chemistries.code"), nullable=False)
    voltage_code = Column(String(2), ForeignKey("nominal_voltages.code"), nullable=False)
    cell_origin_code = Column(String(2), ForeignKey("cell_origins.code"), nullable=False)
    extinguisher_code = Column(String(1), ForeignKey("extinguisher_classes.code"), nullable=False)
    factory_code = Column(String(1), ForeignKey("factory_codes.code"), nullable=False)
    tac_code = Column(String(10), ForeignKey("tac_numbers.code"), nullable=False)
    
    internal_resistance_code = Column(String(10), ForeignKey("internal_resistances.code"), nullable=False)
    warranty_code = Column(String(10), ForeignKey("battery_warranties.code"), nullable=False)
    cell_type_code = Column(String(1), ForeignKey("cell_types.code"), nullable=False)
    pack_construction_code = Column(String(10), ForeignKey("pack_construction_types.code"), nullable=False)
    module_construction_code = Column(String(10), ForeignKey("module_construction_types.code"), nullable=False)
    cooling_code = Column(String(1), ForeignKey("cooling_systems.code"), nullable=False)
    
    num_cells_code = Column(String(10), ForeignKey("number_of_cells.code"), nullable=False)
    weight_code = Column(String(10), ForeignKey("battery_weights.code"), nullable=False)
    dimensions_code = Column(String(20), ForeignKey("dimensions.code"), nullable=False)
    power_80_soc_code = Column(String(10), ForeignKey("power_80_soc.code"), nullable=False)
    power_20_soc_value = Column(Numeric(6, 2), nullable=False)
    carbon_footprint_code = Column(String(10), ForeignKey("carbon_footprints.code"), nullable=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    country = relationship("Country")
    manufacturer = relationship("Manufacturer")
    capacity = relationship("BatteryCapacity")
    chemistry = relationship("BatteryChemistry")
    voltage = relationship("NominalVoltage")
    cell_origin = relationship("CellOrigin")
    extinguisher = relationship("ExtinguisherClass")
    factory = relationship("FactoryCode")
    tac = relationship("TACNumber")
    cell_type = relationship("CellType")
    pack_construction = relationship("PackConstructionType")
    module_construction = relationship("ModuleConstructionType")
    cooling = relationship("CoolingSystem")
    internal_resistance = relationship("InternalResistance")
    warranty = relationship("BatteryWarranty")
    num_cells = relationship("NumberOfCells")
    weight = relationship("BatteryWeight")
    dimensions = relationship("Dimensions")
    power_80_soc = relationship("Power80Soc")
    power_20_soc = relationship("Power20Soc", primaryjoin="foreign(BatteryModel.power_20_soc_value) == remote(Power20Soc.value_kw)", viewonly=True, uselist=False)
    carbon_footprint = relationship("CarbonFootprint")
    bpans = relationship("BPAN", back_populates="model")