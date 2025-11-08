from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.error_handler import ErrorMiddleware
from middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from config.settings import settings
from routes import auth, files, user, health
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Zero-Knowledge Encrypted Storage API",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Setup rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Setup error handlers
ErrorMiddleware.setup_handlers(app)

# Include routers with API v1 prefix
api_prefix = "/api/v1"

app.include_router(auth.router, prefix=api_prefix)
app.include_router(files.router, prefix=api_prefix)
app.include_router(user.router, prefix=api_prefix)
app.include_router(health.router, prefix=api_prefix)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "Documentation disabled in production"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Test database connection
    try:
        from config.database import get_supabase
        client = get_supabase()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )