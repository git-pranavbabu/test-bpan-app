from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LookupTableInfo(BaseModel):
    name: str
    description: str
    code_length: Optional[int] = None


class LookupTableListResponse(BaseModel):
    tables: List[LookupTableInfo]


class CountryBase(BaseModel):
    code: str = Field(..., max_length=2)
    name: str
    region: str


class CountryResponse(CountryBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ManufacturerBase(BaseModel):
    code: str = Field(..., max_length=3)
    name: str
    country_code: str


class ManufacturerResponse(ManufacturerBase):
    created_at: datetime

    class Config:
        from_attributes = True


class BatteryCapacityBase(BaseModel):
    code: str = Field(..., max_length=2)
    value_kwh: float
    description: Optional[str] = None


class BatteryCapacityResponse(BatteryCapacityBase):
    created_at: datetime

    class Config:
        from_attributes = True


class BatteryChemistryBase(BaseModel):
    code: str = Field(..., max_length=1)
    name: str


class BatteryChemistryResponse(BatteryChemistryBase):
    created_at: datetime

    class Config:
        from_attributes = True


class NominalVoltageBase(BaseModel):
    code: str = Field(..., max_length=2)
    value_v: int


class NominalVoltageResponse(NominalVoltageBase):
    created_at: datetime

    class Config:
        from_attributes = True


class CellOriginBase(BaseModel):
    code: str = Field(..., max_length=2)
    country_name: str


class CellOriginResponse(CellOriginBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ExtinguisherClassBase(BaseModel):
    code: str = Field(..., max_length=1)
    class_name: str


class ExtinguisherClassResponse(ExtinguisherClassBase):
    created_at: datetime

    class Config:
        from_attributes = True


class FactoryCodeBase(BaseModel):
    code: str = Field(..., max_length=1)
    factory_name: str
    location: Optional[str] = None


class FactoryCodeResponse(FactoryCodeBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ManufacturingYearBase(BaseModel):
    code: str = Field(..., max_length=1)
    year: int


class ManufacturingYearResponse(ManufacturingYearBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ManufacturingMonthBase(BaseModel):
    code: str = Field(..., max_length=1)
    month_num: int
    name: str


class ManufacturingMonthResponse(ManufacturingMonthBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ManufacturingDateBase(BaseModel):
    code: str = Field(..., max_length=1)
    day_num: int


class ManufacturingDateResponse(ManufacturingDateBase):
    created_at: datetime

    class Config:
        from_attributes = True


class TACNumberBase(BaseModel):
    code: str = Field(..., max_length=10)
    tac_number: str


class TACNumberResponse(TACNumberBase):
    created_at: datetime

    class Config:
        from_attributes = True


class CellTypeBase(BaseModel):
    code: str = Field(..., max_length=1)
    type_name: str


class CellTypeResponse(CellTypeBase):
    created_at: datetime

    class Config:
        from_attributes = True


class ConstructionTypeBase(BaseModel):
    code: str = Field(..., max_length=10)
    construction_type: str


class ConstructionTypeResponse(ConstructionTypeBase):
    created_at: datetime

    class Config:
        from_attributes = True


class CoolingSystemBase(BaseModel):
    code: str = Field(..., max_length=1)
    cooling_type: str


class CoolingSystemResponse(CoolingSystemBase):
    created_at: datetime

    class Config:
        from_attributes = True


