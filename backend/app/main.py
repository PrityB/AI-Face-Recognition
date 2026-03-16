from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import verification, compliance

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(verification.router, prefix=f"{settings.API_V1_STR}/verify", tags=["verification"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}
