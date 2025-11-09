"""
Main FastAPI application
Entry point for the Concise API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.api.v1 import auth, keys, proxy, compress, usage, tale

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Production-ready API for LLM prompt compression with zero context loss",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns the status of the API and its dependencies.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint

    Returns basic API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(
    auth.router,
    prefix="/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    keys.router,
    prefix="/v1/keys",
    tags=["API Keys"]
)

app.include_router(
    proxy.router,
    prefix="/v1",
    tags=["OpenAI Proxy"]
)

app.include_router(
    compress.router,
    prefix="/v1",
    tags=["Compression"]
)

app.include_router(
    usage.router,
    prefix="/v1",
    tags=["Usage & Analytics"]
)

app.include_router(
    tale.router,
    prefix="/v1",
    tags=["TALE Optimization"]
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler

    Catches all unhandled exceptions and returns a generic error response.
    """
    if settings.DEBUG:
        # In debug mode, show the full error
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )
    else:
        # In production, hide error details
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later."
            }
        )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler

    Runs when the application starts.
    """
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler

    Runs when the application shuts down.
    """
    print(f"Shutting down {settings.APP_NAME}")
