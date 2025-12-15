from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes.content import router as content_router
import time
import logging

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

from contextlib import asynccontextmanager
from app.core.database import engine
from app.models.base import Base
# Import all models to ensure they are registered with Base
from app.models import user, content

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"Path: {request.url.path} Method: {request.method} Status: {response.status_code} Duration: {process_time:.4f}s")
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error", "detail": str(exc)},
    )

from app.services.transcript_service import TranscriptNotAvailableError, TranscriptAccessDeniedError

@app.exception_handler(TranscriptNotAvailableError)
async def transcript_not_available_handler(request: Request, exc: TranscriptNotAvailableError):
    logger.warning(f"Transcript not available: {exc.reason}")
    return JSONResponse(
        status_code=400,
        content={
            "error": "TRANSCRIPT_NOT_AVAILABLE",
            "reason": exc.reason
        },
    )

@app.exception_handler(TranscriptAccessDeniedError)
async def transcript_access_denied_handler(request: Request, exc: TranscriptAccessDeniedError):
    logger.warning(f"Transcript access denied: {exc.reason}")
    return JSONResponse(
        status_code=403,
        content={
            "error": "TRANSCRIPT_ACCESS_DENIED",
            "reason": exc.reason
        },
    )

app.include_router(content_router, prefix=f"{settings.API_V1_STR}/content", tags=["content"])

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

@app.get("/")
def root():
    return {"message": "Welcome to Video Repurposing API"}
