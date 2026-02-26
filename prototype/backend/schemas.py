from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Equipment ────────────────────────────────────────────────────────────────

class EquipmentBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    status: Optional[str] = "available"
    quantity: Optional[int] = 1


class EquipmentCreate(EquipmentBase):
    pass


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    quantity: Optional[int] = None


class EquipmentOut(EquipmentBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Element Equipment (junction) ─────────────────────────────────────────────

class ElementEquipmentBase(BaseModel):
    equipment_id: int
    quantity_used: Optional[int] = 1
    notes: Optional[str] = None


class ElementEquipmentCreate(ElementEquipmentBase):
    pass


class ElementEquipmentOut(ElementEquipmentBase):
    id: int
    equipment: Optional[EquipmentOut] = None

    class Config:
        from_attributes = True


# ─── Element ──────────────────────────────────────────────────────────────────

class ElementBase(BaseModel):
    name: str
    type: Optional[str] = "slab"
    description: Optional[str] = None
    volume: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    grade: Optional[str] = None
    water_cement_ratio: Optional[float] = None
    curing_status: Optional[str] = "pending"
    curing_method: Optional[str] = None
    estimated_curing_days: Optional[int] = None
    actual_curing_days: Optional[int] = None
    curing_notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None


class ElementCreate(ElementBase):
    pass


class ElementUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    volume: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    grade: Optional[str] = None
    water_cement_ratio: Optional[float] = None
    curing_status: Optional[str] = None
    curing_method: Optional[str] = None
    estimated_curing_days: Optional[int] = None
    actual_curing_days: Optional[int] = None
    curing_notes: Optional[str] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None


class ElementOut(ElementBase):
    id: int
    project_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    element_equipment: List[ElementEquipmentOut] = []

    class Config:
        from_attributes = True


# ─── Project ──────────────────────────────────────────────────────────────────

class ProjectBase(BaseModel):
    name: str
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = "planning"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    supervisor: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    supervisor: Optional[str] = None


class ProjectOut(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    elements: List[ElementOut] = []

    class Config:
        from_attributes = True


class ProjectSummary(ProjectBase):
    id: int
    created_at: Optional[datetime] = None
    element_count: int = 0

    class Config:
        from_attributes = True


# ─── Curing Suggestion ────────────────────────────────────────────────────────

class CuringSuggestion(BaseModel):
    method: str
    estimated_days: int
    estimated_cost: float
    notes: str
    temperature_requirement: Optional[str] = None
    equipment_recommended: List[str] = []
