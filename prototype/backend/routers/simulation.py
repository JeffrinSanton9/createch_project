"""
=============================================================
  PRECAST YARD SIMULATION  —  FastAPI Router
=============================================================
  Include in your main.py:

      from precast_yard_router import router as precast_router
      app.include_router(precast_router)

  All signals passed as JSON body.
  All monetary values in ₹ INR.
  Every prediction endpoint returns results for ALL 3 curing methods.

  Routes:
      GET  /precast/health
      GET  /precast/signals
      POST /precast/evaluate
      POST /precast/predict/time      (budget → days  × 3 methods)
      POST /precast/predict/cost      (days   → cost  × 3 methods)
      POST /precast/sensitivity/{signal}
=============================================================
"""

from __future__ import annotations

import os
import sys
import time
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field, field_validator

sys.path.insert(0, os.path.dirname(__file__))
from precast_yard_simulation import (
    PrecastYardSimulator,
    YardScenario,
    SIGNAL_RANGES,
    CuringMethod,
    CURING_LABELS,
)

# ─────────────────────────────────────────────────────────────
#  SINGLETON — lazy-train on first request
# ─────────────────────────────────────────────────────────────

_simulator    = PrecastYardSimulator()
_training_sec = 0.0


def _get_simulator() -> PrecastYardSimulator:
    global _training_sec
    if not _simulator._trained:
        t0 = time.perf_counter()
        _simulator.train(n_samples=4000, verbose=False)
        _training_sec = round(time.perf_counter() - t0, 2)
    return _simulator


# ─────────────────────────────────────────────────────────────
#  REQUEST BODY — all scenario signals
# ─────────────────────────────────────────────────────────────

class ScenarioBody(BaseModel):
    """
    All 10 precast yard signals.
    curing_method is NOT an input — results are always returned
    for water, steam, and chemical curing simultaneously.
    """
    num_elements:           int   = Field(50,      ge=5,    le=300,  description="Number of precast elements to produce")
    element_complexity:     float = Field(4.0,     ge=1.0,  le=10.0, description="Complexity 1 (simple slab) → 10 (complex façade); encodes size & dimensions")
    temperature:            float = Field(32.0,    ge=10.0, le=45.0, description="Ambient temperature in °C (Indian sites typically 25–40°C)")
    humidity:               float = Field(65.0,    ge=20.0, le=95.0, description="Relative humidity in % (coastal India can exceed 80%)")
    yard_area_m2:           float = Field(600.0,   ge=100,  le=3000, description="Available casting area in m²")
    equipment_availability: float = Field(0.75,    ge=0.1,  le=1.0,  description="Fraction of full equipment fleet available (0–1)")
    water_budget_liters:    float = Field(40000.0, ge=0,             description="Max water available for curing in litres — if insufficient for water curing, auto-falls back to chemical")
    concrete_m3:            float = Field(200.0,   ge=10,   le=1200, description="Total concrete volume in m³")
    material_unit_cost:     float = Field(6500.0,  ge=5000, le=9000, description="Cost per m³ of concrete in ₹ INR — M25 ≈₹5000, M50 ≈₹9000")
    overhead_pct:           float = Field(0.18,    ge=0.10, le=0.30, description="Overhead as fraction of direct cost (typical India: 15–25%)")

    def to_scenario(self) -> YardScenario:
        _scenario_fields = set(YardScenario.__dataclass_fields__.keys())
        return YardScenario(**{k: v for k, v in self.model_dump().items() if k in _scenario_fields})


class PredictTimeBody(ScenarioBody):
    budget: float = Field(..., gt=0, description="Total available budget in ₹ INR (e.g. 5000000 = ₹50 lakh)")


class PredictCostBody(ScenarioBody):
    days: float = Field(..., gt=0, description="Target completion time in days")


class SensitivityBody(ScenarioBody):
    n_points: int = Field(10, ge=3, le=50, description="Number of sample points along the signal range")


# ─────────────────────────────────────────────────────────────
#  RESPONSE MODELS
# ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status:                str
    model_trained:         bool
    training_time_seconds: float

class SignalInfo(BaseModel):
    name:        str
    type:        str
    min:         float
    max:         float
    description: str

class SignalsResponse(BaseModel):
    signals:              list[SignalInfo]
    curing_methods:       dict[str, str]   # key → label

# One result per curing method
class CuringResult(BaseModel):
    curing_method:  str
    predicted_days: float
    predicted_cost: float

class CuringResultWithConfig(BaseModel):
    curing_method:            str
    predicted_days:           float
    predicted_cost:           float
    recommended_complexity:   float
    recommended_equip:        float

class EvaluateResult(BaseModel):
    curing_method:    str
    predicted_days:   float
    predicted_cost:   float
    groundtruth_days: float
    groundtruth_cost: float

class EvaluateResponse(BaseModel):
    results:  list[EvaluateResult]
    scenario: dict[str, Any]

class PredictTimeResponse(BaseModel):
    input_budget: float
    results:      list[CuringResultWithConfig]
    scenario:     dict[str, Any]

class PredictCostResponse(BaseModel):
    input_days: float
    results:    list[CuringResultWithConfig]
    scenario:   dict[str, Any]

class SensitivityPoint(BaseModel):
    value:            float
    water_days:       float
    water_cost:       float
    steam_days:       float
    steam_cost:       float
    chemical_days:    float
    chemical_cost:    float

class SensitivityResponse(BaseModel):
    signal:  str
    points:  list[SensitivityPoint]
    scenario: dict[str, Any]


# ─────────────────────────────────────────────────────────────
#  SIGNAL METADATA
# ─────────────────────────────────────────────────────────────

_SIGNAL_META: dict[str, dict] = {
    "num_elements":           {"type": "int",   "description": "Number of precast elements to produce"},
    "element_complexity":     {"type": "float", "description": "Complexity 1–10 (encodes element size & dimensions)"},
    "temperature":            {"type": "float", "description": "Ambient temperature in °C (Indian sites 25–40°C)"},
    "humidity":               {"type": "float", "description": "Relative humidity in %"},
    "yard_area_m2":           {"type": "float", "description": "Available casting area in m²"},
    "equipment_availability": {"type": "float", "description": "Fraction of full equipment fleet available (0–1)"},
    "water_budget_liters":    {"type": "float", "description": "Max water for curing — auto-fallback to chemical if insufficient"},
    "concrete_m3":            {"type": "float", "description": "Total concrete volume in m³"},
    "material_unit_cost":     {"type": "float", "description": "Cost per m³ of concrete (₹ INR) — M25 ≈₹5000, M50 ≈₹9000"},
    "overhead_pct":           {"type": "float", "description": "Overhead as fraction of direct cost"},
}


# ─────────────────────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────────────────────

router = APIRouter(prefix="/precast", tags=["Precast Yard Simulation"])


@router.get("/health", response_model=HealthResponse, summary="Model readiness check")
def health():
    sim = _get_simulator()
    return HealthResponse(
        status="ok",
        model_trained=sim._trained,
        training_time_seconds=_training_sec,
    )


@router.get("/signals", response_model=SignalsResponse, summary="All signals with valid ranges")
def list_signals():
    """
    Returns every accepted signal with its valid range, type, and description.
    Use this to build forms dynamically on the frontend.
    Note: curing_method is NOT an input signal — all 3 methods are always evaluated.
    """
    return SignalsResponse(
        signals=[
            SignalInfo(
                name        = name,
                type        = _SIGNAL_META[name]["type"],
                min         = float(lo),
                max         = float(hi),
                description = _SIGNAL_META[name]["description"],
            )
            for name, (lo, hi) in SIGNAL_RANGES.items()
        ],
        curing_methods={str(cm.value): CURING_LABELS[cm] for cm in CuringMethod},
    )


@router.post(
    "/evaluate",
    response_model=EvaluateResponse,
    summary="Predict time & cost for all 3 curing methods",
)
def evaluate(body: ScenarioBody = Body(...)):
    """
    Direct evaluation — returns predicted **and** ground-truth time + cost
    for **all 3 curing methods** (water, steam, chemical) side by side.
    """
    sim     = _get_simulator()
    raw     = sim.evaluate(body.to_scenario())
    return EvaluateResponse(
        results=[EvaluateResult(**r) for r in raw],
        scenario=body.model_dump(),
    )


@router.post(
    "/predict/time",
    response_model=PredictTimeResponse,
    summary="Cost → Time: given a budget, return expected days per curing method",
)
def predict_time(body: PredictTimeBody = Body(...)):
    """
    **Given a budget (₹ INR)**, returns the expected schedule in days
    for each of the 3 curing methods, along with the recommended
    complexity and equipment configuration for that budget.
    """
    sim = _get_simulator()
    raw = sim.predict_time(budget=body.budget, scenario=body.to_scenario(), verbose=False)
    return PredictTimeResponse(
        input_budget = body.budget,
        results      = [CuringResultWithConfig(**r) for r in raw],
        scenario     = body.model_dump(),
    )


@router.post(
    "/predict/cost",
    response_model=PredictCostResponse,
    summary="Time → Cost: given a deadline, return expected cost per curing method",
)
def predict_cost(body: PredictCostBody = Body(...)):
    """
    **Given a target schedule (days)**, returns the expected cost
    for each of the 3 curing methods, along with the recommended
    configuration that meets that deadline.
    """
    sim = _get_simulator()
    raw = sim.predict_cost(days=body.days, scenario=body.to_scenario(), verbose=False)
    return PredictCostResponse(
        input_days = body.days,
        results    = [CuringResultWithConfig(**r) for r in raw],
        scenario   = body.model_dump(),
    )


@router.post(
    "/sensitivity/{signal}",
    response_model=SensitivityResponse,
    summary="Sweep one signal — returns all 3 curing methods at each point",
)
def sensitivity(signal: str, body: SensitivityBody = Body(...)):
    """
    Vary a **single signal** across its full valid range.
    At each point, days and cost are returned for all 3 curing methods —
    ideal for rendering overlaid trade-off curves on the frontend.
    """
    if signal not in SIGNAL_RANGES:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown signal '{signal}'. Valid: {list(SIGNAL_RANGES)}",
        )
    sim = _get_simulator()
    raw = sim.sensitivity(signal=signal, n_points=body.n_points, scenario=body.to_scenario())
    return SensitivityResponse(
        signal   = signal,
        points   = [SensitivityPoint(value=r[signal], **{k: v for k, v in r.items() if k != signal}) for r in raw],
        scenario = body.model_dump(),
    )
