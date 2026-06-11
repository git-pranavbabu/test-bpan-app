from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional
from uuid import UUID
from datetime import datetime, date, timedelta, timezone

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.battery_model import BatteryModel
from app.models.bpan import BPAN, SystemConfig
from app.services.bpan_generator import BPANGenerator, YEAR_CODE_REVERSE, MONTH_CODE_REVERSE, DATE_CODE_REVERSE
from app.services.pdf_generator import generate_pdf
import asyncio

from app.api.v1.endpoints.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/models-for-creation")
def get_models_for_creation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    models = (
        db.query(BatteryModel)
        .options(
            joinedload(BatteryModel.country),
            joinedload(BatteryModel.manufacturer),
            joinedload(BatteryModel.capacity),
            joinedload(BatteryModel.chemistry),
            joinedload(BatteryModel.voltage),
            joinedload(BatteryModel.factory),
        )
        .filter(BatteryModel.is_active == True)
        .all()
    )
    
    result = []
    for m in models:
        result.append({
            "id": str(m.id),
            "name": m.name,
            "country_code": m.country.code,
            "country_name": m.country.name,
            "manufacturer_code": m.manufacturer.code,
            "manufacturer_name": m.manufacturer.name,
            "capacity_code": m.capacity.code,
            "capacity_kwh": float(m.capacity.value_kwh),
            "chemistry_code": m.chemistry.code,
            "chemistry_name": m.chemistry.name,
            "voltage_code": m.voltage.code,
            "voltage_v": m.voltage.value_v,
            "cell_origin_code": m.cell_origin.code if m.cell_origin else "",
            "factory_code": m.factory.code,
            "factory_name": m.factory.factory_name,
        })
    
    return result


@router.get("/last-serial")
def get_last_serial(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    max_serial = db.query(func.max(BPAN.serial_number)).scalar()
    if max_serial:
        return {"serial_number": max_serial}
    config = db.query(SystemConfig).filter(SystemConfig.key == "global_serial").first()
    if config:
        return {"serial_number": int(config.value) - 1}
    return {"serial_number": settings.INITIAL_SERIAL - 1}


@router.post("/generate")
def generate_bpan(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        model_id = UUID(request_data["model_id"])
    except (KeyError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid or missing model_id")
    
    factory_code = request_data.get("factory_code")
    if not factory_code:
        raise HTTPException(status_code=400, detail="Missing factory_code")
    
    custom_date_str = request_data.get("custom_date")
    
    if custom_date_str:
        try:
            custom_date = date.fromisoformat(custom_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    else:
        custom_date = None
    
    model = (
        db.query(BatteryModel)
        .options(
            joinedload(BatteryModel.country),
            joinedload(BatteryModel.manufacturer),
            joinedload(BatteryModel.capacity),
            joinedload(BatteryModel.chemistry),
            joinedload(BatteryModel.voltage),
            joinedload(BatteryModel.cell_origin),
            joinedload(BatteryModel.extinguisher),
            joinedload(BatteryModel.factory),
        )
        .filter(BatteryModel.id == model_id, BatteryModel.is_active == True)
        .first()
    )
    if not model:
        raise HTTPException(status_code=404, detail="Active model not found")
    
    if custom_date:
        manufacturing_date = custom_date
    else:
        manufacturing_date = date.today()
    
    generator = BPANGenerator(db)
    result = generator.generate(
        model=model,
        factory_code=factory_code,
        manufacturing_date=manufacturing_date,
        created_by=current_user.id,
    )
    
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=400, detail=result["error"])


@router.get("/global-serial")
def get_global_serial(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    config = db.query(SystemConfig).filter(SystemConfig.key == "global_serial").first()
    max_serial = db.query(func.max(BPAN.serial_number)).scalar() or 0
    current = int(config.value) if config else settings.INITIAL_SERIAL
    next_serial = max(max_serial + 1, current)
    return {
        "current": current,
        "next_serial": next_serial,
        "max_used": max_serial,
    }


@router.put("/global-serial")
def set_global_serial(
    data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        new_value = int(data.get("value", 0))
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid serial number value")
    if new_value < 1:
        raise HTTPException(status_code=400, detail="Serial must be at least 1")
    
    existing = db.query(BPAN).filter(BPAN.serial_number == new_value).first()
    max_serial = db.query(func.max(BPAN.serial_number)).scalar() or 0
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Serial {new_value} has already been used. Last used serial is {max_serial}."
        )
    if new_value <= max_serial:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot set serial to {new_value}. It must be greater than the last used serial ({max_serial})."
        )
    
    config = db.query(SystemConfig).filter(SystemConfig.key == "global_serial").first()
    if config:
        config.value = str(new_value)
    else:
        config = SystemConfig(key="global_serial", value=str(new_value))
        db.add(config)
    db.commit()
    return {"message": f"Global serial set to {new_value}", "value": new_value}


@router.put("/{code}")
def edit_bpan(
    code: str,
    request_data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    bpan_record = db.query(BPAN).filter(BPAN.code_21char == code).first()
    if not bpan_record:
        raise HTTPException(status_code=404, detail="BPAN not found")
    
    new_model_id = request_data.get("model_id")
    new_date_str = request_data.get("manufacturing_date")
    
    if new_model_id:
        try:
            bpan_record.model_id = UUID(new_model_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid model_id format")
    
    if new_date_str:
        try:
            new_date = date.fromisoformat(new_date_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
        bpan_record.year_code = YEAR_CODE_REVERSE.get(new_date.year, '1')
        bpan_record.month_code = MONTH_CODE_REVERSE.get(new_date.month, 'A')
        bpan_record.date_code = DATE_CODE_REVERSE.get(new_date.day, '1')
    
    model = (
        db.query(BatteryModel)
        .options(
            joinedload(BatteryModel.country),
            joinedload(BatteryModel.manufacturer),
            joinedload(BatteryModel.capacity),
            joinedload(BatteryModel.chemistry),
            joinedload(BatteryModel.voltage),
            joinedload(BatteryModel.cell_origin),
            joinedload(BatteryModel.extinguisher),
            joinedload(BatteryModel.factory),
            joinedload(BatteryModel.tac),
            joinedload(BatteryModel.cell_type),
            joinedload(BatteryModel.pack_construction),
            joinedload(BatteryModel.module_construction),
            joinedload(BatteryModel.cooling),
            joinedload(BatteryModel.internal_resistance),
            joinedload(BatteryModel.weight),
            joinedload(BatteryModel.warranty),
            joinedload(BatteryModel.num_cells),
            joinedload(BatteryModel.dimensions),
            joinedload(BatteryModel.power_80_soc),
            joinedload(BatteryModel.power_20_soc),
            joinedload(BatteryModel.carbon_footprint),
        )
        .filter(BatteryModel.id == bpan_record.model_id)
        .first()
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    factory_code = model.factory.code
    serial_number = bpan_record.serial_number
    
    if not model.cell_origin or not model.extinguisher:
        raise HTTPException(
            status_code=400,
            detail="Cannot update BPAN: Cell Origin or Extinguisher class lookup entry is missing on the associated battery model."
        )
        
    cell_origin_code = model.cell_origin.code
    extinguisher_code = model.extinguisher.code
    
    new_code = (
        f"{model.country.code}"
        f"{model.manufacturer.code}"
        f"{model.capacity.code}"
        f"{model.chemistry.code}"
        f"{model.voltage.code}"
        f"{cell_origin_code}"
        f"{extinguisher_code}"
        f"{bpan_record.year_code}"
        f"{bpan_record.month_code}"
        f"{bpan_record.date_code}"
        f"{factory_code}"
        f"{str(serial_number).zfill(4)}"
    )
    
    if new_code != code:
        existing = db.query(BPAN).filter(BPAN.code_21char == new_code).first()
        if existing:
            raise HTTPException(status_code=400, detail="BPAN code already exists")
        bpan_record.code_21char = new_code
    
    db.commit()
    db.refresh(bpan_record)
    
    return {
        "message": "BPAN updated successfully",
        "code_21char": bpan_record.code_21char,
        "manufacturing_date": f"{bpan_record.year_code}-{bpan_record.month_code}-{bpan_record.date_code}",
        "serial_number": serial_number,
    }


@router.get("/default-date")
def get_default_date(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    config = db.query(SystemConfig).filter(SystemConfig.key == "manufacturing_date").first()
    return {"date": config.value if config else None}


@router.post("/default-date")
def set_default_date(
    data: dict,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    config = db.query(SystemConfig).filter(SystemConfig.key == "manufacturing_date").first()
    date_val = data.get("date")
    if config:
        config.value = date_val
    else:
        config = SystemConfig(key="manufacturing_date", value=date_val)
        db.add(config)
    db.commit()
    return {"message": "Default date saved"}


@router.get("/stats")
def get_bpan_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    weekday = now.weekday()
    week_start = today_start - timedelta(days=weekday)
    last_week_end = week_start - timedelta(days=1)
    last_week_start = last_week_end - timedelta(days=6)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    today_count = db.query(BPAN).filter(BPAN.created_at >= today_start).count()
    week_count = db.query(BPAN).filter(BPAN.created_at >= week_start).count()
    last_week_count = db.query(BPAN).filter(
        BPAN.created_at >= last_week_start,
        BPAN.created_at < week_start
    ).count()
    month_count = db.query(BPAN).filter(BPAN.created_at >= month_start).count()
    
    return {
        "today": today_count,
        "this_week": week_count,
        "last_week": last_week_count,
        "this_month": month_count,
    }


@router.get("/reports")
def get_reports(
    q: Optional[str] = None,
    model_name: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    serial_from: Optional[int] = None,
    serial_to: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(BPAN).options(joinedload(BPAN.model))
    
    if q:
        query = query.filter(
            BPAN.code_21char.ilike(f"%{q}%")
        )
    
    if model_name:
        query = query.join(BPAN.model).filter(
            BatteryModel.name.ilike(f"%{model_name}%")
        )
    
    if date_from:
        query = query.filter(BPAN.created_at >= date_from)
    
    if date_to:
        query = query.filter(BPAN.created_at < date_to + timedelta(days=1))
    
    if serial_from is not None:
        query = query.filter(BPAN.serial_number >= serial_from)
    
    if serial_to is not None:
        query = query.filter(BPAN.serial_number <= serial_to)
    
    total_count = query.count()
    bpans = query.order_by(BPAN.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": [
            {
                "code_21char": b.code_21char,
                "model_name": b.model.name,
                "serial_number": b.serial_number,
                "created_at": b.created_at.isoformat(),
            }
            for b in bpans
        ],
        "total": total_count,
        "skip": skip,
        "limit": limit
    }




@router.get("/{code}")
def get_bpan(
    code: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bpan_record = (
        db.query(BPAN)
        .options(
            joinedload(BPAN.model).joinedload(BatteryModel.country),
            joinedload(BPAN.model).joinedload(BatteryModel.manufacturer),
            joinedload(BPAN.model).joinedload(BatteryModel.capacity),
            joinedload(BPAN.model).joinedload(BatteryModel.chemistry),
            joinedload(BPAN.model).joinedload(BatteryModel.voltage),
            joinedload(BPAN.model).joinedload(BatteryModel.cell_origin),
            joinedload(BPAN.model).joinedload(BatteryModel.extinguisher),
            joinedload(BPAN.model).joinedload(BatteryModel.factory),
            joinedload(BPAN.model).joinedload(BatteryModel.tac),
            joinedload(BPAN.model).joinedload(BatteryModel.cell_type),
            joinedload(BPAN.model).joinedload(BatteryModel.pack_construction),
            joinedload(BPAN.model).joinedload(BatteryModel.module_construction),
            joinedload(BPAN.model).joinedload(BatteryModel.cooling),
            joinedload(BPAN.model).joinedload(BatteryModel.internal_resistance),
            joinedload(BPAN.model).joinedload(BatteryModel.weight),
            joinedload(BPAN.model).joinedload(BatteryModel.warranty),
            joinedload(BPAN.model).joinedload(BatteryModel.num_cells),
            joinedload(BPAN.model).joinedload(BatteryModel.dimensions),
            joinedload(BPAN.model).joinedload(BatteryModel.power_80_soc),
            joinedload(BPAN.model).joinedload(BatteryModel.power_20_soc),
            joinedload(BPAN.model).joinedload(BatteryModel.carbon_footprint),
            joinedload(BPAN.year),
            joinedload(BPAN.month),
            joinedload(BPAN.date),
        )
        .filter(BPAN.code_21char == code)
        .first()
    )
    
    if not bpan_record:
        raise HTTPException(status_code=404, detail="BPAN not found")
    
    return bpan_record


@router.get("/{code}/pdf")
async def get_bpan_pdf(
    code: str,
    password: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bpan_record = (
        db.query(BPAN)
        .options(
            joinedload(BPAN.model).joinedload(BatteryModel.country),
            joinedload(BPAN.model).joinedload(BatteryModel.manufacturer),
            joinedload(BPAN.model).joinedload(BatteryModel.capacity),
            joinedload(BPAN.model).joinedload(BatteryModel.chemistry),
            joinedload(BPAN.model).joinedload(BatteryModel.voltage),
            joinedload(BPAN.model).joinedload(BatteryModel.cell_origin),
            joinedload(BPAN.model).joinedload(BatteryModel.extinguisher),
            joinedload(BPAN.model).joinedload(BatteryModel.factory),
            joinedload(BPAN.model).joinedload(BatteryModel.tac),
            joinedload(BPAN.model).joinedload(BatteryModel.cell_type),
            joinedload(BPAN.model).joinedload(BatteryModel.pack_construction),
            joinedload(BPAN.model).joinedload(BatteryModel.module_construction),
            joinedload(BPAN.model).joinedload(BatteryModel.cooling),
            joinedload(BPAN.model).joinedload(BatteryModel.internal_resistance),
            joinedload(BPAN.model).joinedload(BatteryModel.weight),
            joinedload(BPAN.model).joinedload(BatteryModel.warranty),
            joinedload(BPAN.model).joinedload(BatteryModel.num_cells),
            joinedload(BPAN.model).joinedload(BatteryModel.dimensions),
            joinedload(BPAN.model).joinedload(BatteryModel.power_80_soc),
            joinedload(BPAN.model).joinedload(BatteryModel.power_20_soc),
            joinedload(BPAN.model).joinedload(BatteryModel.carbon_footprint),
            joinedload(BPAN.year),
            joinedload(BPAN.month),
            joinedload(BPAN.date),
        )
        .filter(BPAN.code_21char == code)
        .first()
    )
    
    if not bpan_record:
        raise HTTPException(status_code=404, detail="BPAN not found")
    
    pdf_buffer = await asyncio.to_thread(generate_pdf, bpan_record, password=password)
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]), 
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=BPAN_{code}.pdf"
        }
    )

