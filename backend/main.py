from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import engine, Base

import models.task  # registers models

from routers.task_router import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For SQLite (local dev) – create tables automatically.
    # For PostgreSQL (production) – Alembic migrations handle the schema;
    # create_all is skipped to avoid conflicts with the migration history.
    if settings.DATABASE_URL.startswith("sqlite"):
       Base.metadata.create_all(bind=engine)
       print(f"✅ SQLite tables created ({settings.DATABASE_URL})")
    else:
       print(f"✅ Using PostgreSQL – initializing schema")
       Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "A production-ready Task Management REST API built with FastAPI, "
        "SQLAlchemy, and Pydantic v2."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(task_router)


@app.get("/", tags=["Health"])
def root():
    return JSONResponse(
        content={
            "success": True,
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "message": "TaskFlow API is running 🚀",
            "docs": "/docs",
        }
    )


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}