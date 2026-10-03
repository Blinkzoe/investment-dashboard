from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.imports import router as imports_router
from app.api.routes.import_transactions import router as import_transactions_router
from app.api.routes.positions import router as positions_router
from app.api.routes.portfolio import router as portfolio_router
from app.api.routes.reconciliation import router as reconciliation_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.snapshots import router as snapshots_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url="/redoc" if settings.app_env != "production" else None,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(imports_router)
app.include_router(import_transactions_router)
app.include_router(positions_router)
app.include_router(portfolio_router)
app.include_router(reconciliation_router)
app.include_router(transactions_router)
app.include_router(snapshots_router)
