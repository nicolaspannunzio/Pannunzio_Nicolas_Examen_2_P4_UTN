from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session
from app.core.database import create_db_and_tables, engine
from app.core.seed import seed_unidades_medida
from app.modules.unidades_medida.router import router as unidades_router
from app.modules.categorias.router import router as categorias_router
from app.modules.productos.router import router as productos_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Crear tablas si no existen
    create_db_and_tables()
    # 2. Ejecutar seed de unidades de medida
    with Session(engine) as session:
        seed_unidades_medida(session)
    yield

app = FastAPI(
    title="Food Store API",
    description="Catálogo de Productos - Programación IV (Parcial 2)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS habilitado para Vite (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers modulares
app.include_router(unidades_router)
app.include_router(categorias_router)
app.include_router(productos_router)

@app.get("/")
def root():
    return {"message": "Food Store API activa. Documentación en /docs"}