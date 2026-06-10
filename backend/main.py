from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import alternatives, calculation, criteria, imports, scores

app = FastAPI(title="VIKOR Backend API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(alternatives.router, prefix="/api")
app.include_router(criteria.router, prefix="/api")
app.include_router(scores.router, prefix="/api")
app.include_router(calculation.router, prefix="/api")
app.include_router(imports.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "VIKOR Backend API berjalan"}
