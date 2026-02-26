from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas
from core_logic import suggest_curing_method

router = APIRouter(prefix="/projects/{project_id}/elements", tags=["Elements"])


@router.get("/", response_model=List[schemas.ElementOut])
def list_elements(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.elements


@router.post("/", response_model=schemas.ElementOut, status_code=201)
def create_element(project_id: int, element: schemas.ElementCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_element = models.Element(project_id=project_id, **element.model_dump())
    db.add(db_element)
    db.commit()
    db.refresh(db_element)
    return db_element


@router.get("/{element_id}", response_model=schemas.ElementOut)
def get_element(project_id: int, element_id: int, db: Session = Depends(get_db)):
    element = db.query(models.Element).filter(
        models.Element.id == element_id,
        models.Element.project_id == project_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    return element


@router.put("/{element_id}", response_model=schemas.ElementOut)
def update_element(project_id: int, element_id: int, update: schemas.ElementUpdate, db: Session = Depends(get_db)):
    element = db.query(models.Element).filter(
        models.Element.id == element_id,
        models.Element.project_id == project_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(element, field, value)
    db.commit()
    db.refresh(element)
    return element


@router.delete("/{element_id}", status_code=204)
def delete_element(project_id: int, element_id: int, db: Session = Depends(get_db)):
    element = db.query(models.Element).filter(
        models.Element.id == element_id,
        models.Element.project_id == project_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")
    db.delete(element)
    db.commit()


# ─── Curing Suggestion ────────────────────────────────────────────────────────

@router.get("/{element_id}/curing-suggestion", response_model=schemas.CuringSuggestion)
def get_curing_suggestion(project_id: int, element_id: int, db: Session = Depends(get_db)):
    """
    Returns a curing method suggestion based on element properties.
    Currently rule-based (IS456). AI model will be plugged in later.
    """
    element = db.query(models.Element).filter(
        models.Element.id == element_id,
        models.Element.project_id == project_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")

    suggestion = suggest_curing_method(
        element_type=element.type,
        grade=element.grade,
        volume=element.volume,
        water_cement_ratio=element.water_cement_ratio,
    )
    return suggestion


# ─── Element Equipment ────────────────────────────────────────────────────────

@router.post("/{element_id}/equipment", response_model=schemas.ElementEquipmentOut, status_code=201)
def add_equipment_to_element(
    project_id: int, element_id: int,
    payload: schemas.ElementEquipmentCreate,
    db: Session = Depends(get_db)
):
    element = db.query(models.Element).filter(
        models.Element.id == element_id,
        models.Element.project_id == project_id
    ).first()
    if not element:
        raise HTTPException(status_code=404, detail="Element not found")

    equipment = db.query(models.Equipment).filter(models.Equipment.id == payload.equipment_id).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    ee = models.ElementEquipment(element_id=element_id, **payload.model_dump())
    db.add(ee)
    db.commit()
    db.refresh(ee)
    return ee


@router.delete("/{element_id}/equipment/{ee_id}", status_code=204)
def remove_equipment_from_element(
    project_id: int, element_id: int, ee_id: int,
    db: Session = Depends(get_db)
):
    ee = db.query(models.ElementEquipment).filter(
        models.ElementEquipment.id == ee_id,
        models.ElementEquipment.element_id == element_id
    ).first()
    if not ee:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(ee)
    db.commit()
