from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class ElementType(str, enum.Enum):
    SLAB = "slab"
    BEAM = "beam"
    COLUMN = "column"
    CEILING = "ceiling"
    WALL = "wall"
    FOUNDATION = "foundation"
    OTHER = "other"


class CuringStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="available")  # available, in_use, maintenance
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String, default=ProjectStatus.PLANNING)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    supervisor = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    elements = relationship("Element", back_populates="project", cascade="all, delete-orphan")


class Element(Base):
    __tablename__ = "elements"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, default=ElementType.SLAB)
    description = Column(Text, nullable=True)

    # Physical dimensions
    volume = Column(Float, nullable=True)       # cubic meters
    length = Column(Float, nullable=True)       # meters
    width = Column(Float, nullable=True)        # meters
    height = Column(Float, nullable=True)       # meters

    # Mix details
    grade = Column(String, nullable=True)       # e.g. M25, M30 (IS456 grades)
    water_cement_ratio = Column(Float, nullable=True)

    # Curing details
    curing_status = Column(String, default=CuringStatus.PENDING)
    curing_method = Column(String, nullable=True)   # suggested by backend logic
    estimated_curing_days = Column(Integer, nullable=True)
    actual_curing_days = Column(Integer, nullable=True)
    curing_notes = Column(Text, nullable=True)

    # Cost
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="elements")
    element_equipment = relationship("ElementEquipment", back_populates="element", cascade="all, delete-orphan")


class ElementEquipment(Base):
    __tablename__ = "element_equipment"

    id = Column(Integer, primary_key=True, index=True)
    element_id = Column(Integer, ForeignKey("elements.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    quantity_used = Column(Integer, default=1)
    notes = Column(Text, nullable=True)

    element = relationship("Element", back_populates="element_equipment")
    equipment = relationship("Equipment")
