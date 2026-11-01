from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import router
from app.database.session import init_db
from app.utils.config import get_settings
from app.utils.rate_limit import RateLimitMiddleware
from app.utils.security import scrub_sensitive_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Production-style MVP AI Security Firewall for Large Language Models.",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        location = error.get("loc", [])
        field = ".".join(str(item) for item in location[1:]) if len(location) > 1 else "body"
        errors.append(
            {
                "field": field,
                "message": error.get("msg", "Invalid request"),
                "type": error.get("type"),
            }
        )
    return JSONResponse(status_code=422, content={"detail": "Request validation failed", "errors": errors})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    cleaned_exc = scrub_sensitive_data(str(exc))
    if settings.debug:
        return JSONResponse(status_code=500, content={"detail": "Internal server error", "error": cleaned_exc})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
