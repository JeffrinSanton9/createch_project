"""
core_logic.py
─────────────
Curing method suggestion engine for concrete elements.
This is a placeholder — the actual AI/ML model will be plugged in later.
Currently uses rule-based logic derived from IS456 standards.
"""

from schemas import CuringSuggestion


# IS456 minimum curing periods (days) by grade
GRADE_CURING_DAYS = {
    "M10": 7, "M15": 7, "M20": 7,
    "M25": 14, "M30": 14, "M35": 14,
    "M40": 14, "M45": 14, "M50": 28,
}

CURING_METHODS = {
    "ponding": {
        "name": "Ponding / Immersion",
        "cost_per_m3": 150,
        "notes": "Suitable for slabs and flat surfaces. Water is retained on the surface for the curing period.",
        "equipment": ["Water pump", "Polythene sheets", "Sand bunds"],
    },
    "wet_covering": {
        "name": "Wet Covering (Hessian/Gunny)",
        "cost_per_m3": 100,
        "notes": "Wet jute or hessian cloth is wrapped around the element and kept moist.",
        "equipment": ["Hessian cloth", "Water tanker", "Sprinkler"],
    },
    "curing_compound": {
        "name": "Curing Compound Application",
        "cost_per_m3": 200,
        "notes": "Chemical curing compound sprayed immediately after formwork removal. Good for columns/walls.",
        "equipment": ["Spray pump", "Curing compound (membrane-forming)"],
    },
    "steam_curing": {
        "name": "Steam Curing",
        "cost_per_m3": 500,
        "notes": "Accelerated curing using steam. Used for precast elements needing fast turnaround.",
        "equipment": ["Steam boiler", "Steam pipes", "Enclosure covers"],
    },
    "sprinkler": {
        "name": "Continuous Sprinkler / Fog Misting",
        "cost_per_m3": 120,
        "notes": "Continuous fine water mist sprayed over the element surface.",
        "equipment": ["Sprinkler system", "Water pump", "Timer control"],
    },
}


def suggest_curing_method(
    element_type: str,
    grade: str | None,
    volume: float | None,
    water_cement_ratio: float | None,
) -> CuringSuggestion:
    """
    Rule-based curing suggestion.
    TODO: Replace with AI model inference when ready.
    """

    grade = (grade or "M25").upper()
    volume = volume or 1.0
    element_type = (element_type or "slab").lower()

    # Determine base curing days from grade
    base_days = GRADE_CURING_DAYS.get(grade, 14)

    # Select method by element type
    if element_type in ("slab", "foundation"):
        method_key = "ponding"
    elif element_type in ("beam",):
        method_key = "wet_covering"
    elif element_type in ("column", "wall"):
        method_key = "curing_compound"
    elif element_type == "ceiling":
        method_key = "sprinkler"
    else:
        method_key = "wet_covering"

    # High-grade concrete → consider steam curing for precast
    if grade in ("M40", "M45", "M50") and element_type in ("beam", "column"):
        method_key = "steam_curing"
        base_days = max(base_days - 7, 7)  # Steam curing accelerates

    method = CURING_METHODS[method_key]
    estimated_cost = round(method["cost_per_m3"] * volume, 2)

    temperature_note = None
    if water_cement_ratio and water_cement_ratio < 0.4:
        temperature_note = "Low w/c ratio detected — ensure ambient temperature stays above 10°C during curing."

    return CuringSuggestion(
        method=method["name"],
        estimated_days=base_days,
        estimated_cost=estimated_cost,
        notes=method["notes"],
        temperature_requirement=temperature_note,
        equipment_recommended=method["equipment"],
    )
