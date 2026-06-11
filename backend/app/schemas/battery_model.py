from pydantic import BaseModel, Field
from typing import Optional

class BatteryModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    country_code: str = Field(..., max_length=2)
    manufacturer_code: str = Field(..., max_length=3)
    capacity_code: str = Field(..., max_length=2)
    chemistry_code: str = Field(..., max_length=1)
    voltage_code: str = Field(..., max_length=2)
    cell_origin_code: str = Field(..., max_length=2)
    extinguisher_code: str = Field(..., max_length=1)
    factory_code: str = Field(..., max_length=1)
    tac_code: str = Field(..., max_length=10)
    internal_resistance_code: str = Field(..., max_length=10)
    warranty_code: str = Field(..., max_length=10)
    cell_type_code: str = Field(..., max_length=1)
    pack_construction_code: str = Field(..., max_length=10)
    module_construction_code: str = Field(..., max_length=10)
    cooling_code: str = Field(..., max_length=1)
    num_cells_code: str = Field(..., max_length=10)
    weight_code: str = Field(..., max_length=10)
    dimensions_code: str = Field(..., max_length=20)
    power_80_soc_code: str = Field(..., max_length=10)
    power_20_soc_value: float
    carbon_footprint_code: str = Field(..., max_length=10)

class BatteryModelCreate(BatteryModelBase):
    pass

class BatteryModelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    country_code: Optional[str] = Field(None, max_length=2)
    manufacturer_code: Optional[str] = Field(None, max_length=3)
    capacity_code: Optional[str] = Field(None, max_length=2)
    chemistry_code: Optional[str] = Field(None, max_length=1)
    voltage_code: Optional[str] = Field(None, max_length=2)
    cell_origin_code: Optional[str] = Field(None, max_length=2)
    extinguisher_code: Optional[str] = Field(None, max_length=1)
    factory_code: Optional[str] = Field(None, max_length=1)
    tac_code: Optional[str] = Field(None, max_length=10)
    internal_resistance_code: Optional[str] = Field(None, max_length=10)
    warranty_code: Optional[str] = Field(None, max_length=10)
    cell_type_code: Optional[str] = Field(None, max_length=1)
    pack_construction_code: Optional[str] = Field(None, max_length=10)
    module_construction_code: Optional[str] = Field(None, max_length=10)
    cooling_code: Optional[str] = Field(None, max_length=1)
    num_cells_code: Optional[str] = Field(None, max_length=10)
    weight_code: Optional[str] = Field(None, max_length=10)
    dimensions_code: Optional[str] = Field(None, max_length=20)
    power_80_soc_code: Optional[str] = Field(None, max_length=10)
    power_20_soc_value: Optional[float] = None
    carbon_footprint_code: Optional[str] = Field(None, max_length=10)
    is_active: Optional[bool] = None
