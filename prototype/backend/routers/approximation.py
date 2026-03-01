from fastapi import APIRouter, Body
from pydantic import BaseModel
from typing import List, Literal
from approximation_technique.linear_regression import linear_regression
from approximation_technique.polynomial_regression import polynomial_regression

router = APIRouter(prefix="/approximation", tags=["Approximation"])

class ApproximationRequest(BaseModel):
    points: List[List[float]]  # [[x1, y1], [x2, y2], ...]
    method: Literal["linear", "polynomial"] = "linear"
    degree: int = 3# Only used for polynomial

class ApproximationResponse(BaseModel):
    function: str

@router.post("/fit", response_model=ApproximationResponse)
def fit_approximation(req: ApproximationRequest = Body(...)):
    if req.method == "linear":
        func_str = linear_regression(req.points, len(req.points))
    elif req.method == "polynomial":
        func_str = polynomial_regression(req.points, req.degree)
    else:
        raise ValueError("Unknown method")
    return {"function": func_str}
