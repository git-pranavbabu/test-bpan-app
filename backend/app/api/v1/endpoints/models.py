from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.battery_model import BatteryModel
from app.schemas.battery_model import BatteryModelCreate, BatteryModelUpdate
from app.api.v1.endpoints.auth import get_current_user, require_admin

router = APIRouter()


@router.get("/")
def list_models(
    current_user: User = Depends(require_admin),
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
        .all()
    )
    return models


@router.get("/{model_id}")
def get_model(
    model_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
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
            joinedload(BatteryModel.carbon_footprint),
        )
        .filter(BatteryModel.id == model_id)
        .first()
    )
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/")
def create_model(
    model_in: BatteryModelCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(BatteryModel).filter(BatteryModel.name == model_in.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model with this name already exists")
    
    model = BatteryModel(**model_in.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)
    return model


@router.put("/{model_id}")
def update_model(
    model_id: UUID,
    model_in: BatteryModelUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    model = db.query(BatteryModel).filter(BatteryModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    update_data = model_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(model, key, value)
    
    db.commit()
    db.refresh(model)
    return model


@router.delete("/{model_id}")
def deactivate_model(
    model_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    model = db.query(BatteryModel).filter(BatteryModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model.is_active = False
    db.commit()
    return {"message": "Model deactivated successfully"}


@router.patch("/{model_id}/activate")
def activate_model(
    model_id: UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    model = db.query(BatteryModel).filter(BatteryModel.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model.is_active = True
    db.commit()
    return {"message": "Model activated successfully"}
