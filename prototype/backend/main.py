from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
import models
from routers import projects, elements, equipment, simulation, approximation

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Precast Yard — Curing Optimizer API",
    description="Backend API for L&T Precast Yard concrete curing optimization.",
    version="0.1.0",
)

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(elements.router, prefix="/api")
app.include_router(equipment.router, prefix="/api")
app.include_router(simulation.router, prefix="/api")
app.include_router(approximation.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Precast Yard API is running.", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
