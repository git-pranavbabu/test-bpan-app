from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import date
from uuid import UUID

from app.core.bpan_lookups import (
    YEAR_CODES,
    MONTH_CODES,
    DATE_CODES,
)
from app.models.battery_model import BatteryModel
from app.models.bpan import BPAN, SystemConfig
from app.core.config import settings

YEAR_CODE_REVERSE = {v: k for k, v in YEAR_CODES.items()}
MONTH_CODE_REVERSE = {
    1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E', 6: 'F',
    7: 'G', 8: 'H', 9: 'J', 10: 'K', 11: 'L', 12: 'M'
}
DATE_CODE_REVERSE = {v: k for k, v in DATE_CODES.items()}


class BPANGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def _get_date_code(self, day: int) -> str:
        return DATE_CODE_REVERSE.get(day, '1')
    
    def _get_next_serial(self) -> int:
        # Acquire a transaction-level advisory lock (ID 12345) to prevent concurrent
        # requests from generating the same serial number. This lock is automatically
        # released when the transaction commits or rolls back.
        self.db.execute(text("SELECT pg_advisory_xact_lock(12345)"))
        
        max_serial = self.db.query(func.max(BPAN.serial_number)).scalar() or 0
        config = self.db.query(SystemConfig).filter(SystemConfig.key == "global_serial").first()
        global_serial = int(config.value) if config else settings.INITIAL_SERIAL
        
        if max_serial > 0:
            next_serial = max(max_serial + 1, global_serial)
        else:
            next_serial = global_serial
        
        return 1 if next_serial > 9999 else next_serial
    
    def _assemble_21char_code(
        self,
        country_code: str,
        manufacturer_code: str,
        capacity_code: str,
        chemistry_code: str,
        voltage_code: str,
        cell_origin_code: str,
        extinguisher_code: str,
        year_code: str,
        month_code: str,
        date_code: str,
        factory_code: str,
        serial_number: int,
    ) -> str:
        serial_str = str(serial_number).zfill(4)
        return (
            f"{country_code}"
            f"{manufacturer_code}"
            f"{capacity_code}"
            f"{chemistry_code}"
            f"{voltage_code}"
            f"{cell_origin_code}"
            f"{extinguisher_code}"
            f"{year_code}"
            f"{month_code}"
            f"{date_code}"
            f"{factory_code}"
            f"{serial_str}"
        )
    
    def generate(
        self,
        model: BatteryModel,
        factory_code: str,
        manufacturing_date: date,
        created_by: UUID,
    ) -> dict:
        try:
            country_code = model.country.code
            manufacturer_code = model.manufacturer.code
            capacity_code = model.capacity.code
            chemistry_code = model.chemistry.code
            voltage_code = model.voltage.code
            cell_origin_code = model.cell_origin.code
            extinguisher_code = model.extinguisher.code
            
            year_code = YEAR_CODE_REVERSE.get(manufacturing_date.year, '1')
            month_code = MONTH_CODE_REVERSE.get(manufacturing_date.month, 'A')
            date_code = self._get_date_code(manufacturing_date.day)
            
            serial_number = self._get_next_serial()
            
            code_21char = self._assemble_21char_code(
                country_code=country_code,
                manufacturer_code=manufacturer_code,
                capacity_code=capacity_code,
                chemistry_code=chemistry_code,
                voltage_code=voltage_code,
                cell_origin_code=cell_origin_code,
                extinguisher_code=extinguisher_code,
                year_code=year_code,
                month_code=month_code,
                date_code=date_code,
                factory_code=factory_code,
                serial_number=serial_number,
            )
            
            existing = self.db.query(BPAN).filter(BPAN.code_21char == code_21char).first()
            if existing:
                return {"success": False, "error": "BPAN code already exists"}
            
            bpan_record = BPAN(
                code_21char=code_21char,
                model_id=model.id,
                year_code=year_code,
                month_code=month_code,
                date_code=date_code,
                serial_number=serial_number,
                created_by=created_by,
            )
            
            self.db.add(bpan_record)
            self.db.commit()
            self.db.refresh(bpan_record)
            
            return {
                "success": True,
                "id": str(bpan_record.id),
                "code_21char": code_21char,
                "serial_number": serial_number,
                "manufacturing_date": manufacturing_date.isoformat(),
            }
        
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
