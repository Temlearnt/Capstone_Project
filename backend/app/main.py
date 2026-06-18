from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .routers import upload, status, result, history, auth, test_db
from .db.operations import test_connection
from .routers import screen
from .routers import dashboard
from .routers import job_roles
from .routers import profile
from .routers import candidates



# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Recruitly API...")
    
    # Test database connection
    if test_connection():
        logger.info("✅ Database connected successfully")
    else:
        logger.warning("⚠️ Database connection failed! Check your SUPABASE_URL and SUPABASE_KEY")
    
    logger.info(f"📊 MLflow tracking URI: {settings.MLFLOW_TRACKING_URI}")
    logger.info(f"CORS_ORIGINS value: {settings.CORS_ORIGINS}")
    logger.info(f"CORS_ORIGINS type: {type(settings.CORS_ORIGINS)}")
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Recruitly API...")

# Create FastAPI app
app = FastAPI(
    title="Recruitly API",
    version="1.0.0",
    description="AI-based CV screening and ranking API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(status.router, prefix="/status", tags=["Status"])
app.include_router(result.router, prefix="/result", tags=["Result"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(test_db.router, prefix="/test", tags=["Test"])
app.include_router(screen.router, prefix="/screen", tags=["Screening"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(job_roles.router)
app.include_router(profile.router)
app.include_router(candidates.router)



@app.get("/")
async def root():
    return {
        "message": "Welcome to Recruitly API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}