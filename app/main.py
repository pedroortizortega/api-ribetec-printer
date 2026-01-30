from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import print_router

settings = get_settings()

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    description="API para imprimir etiquetas en impresora térmica Ribetec RT-420ME",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(print_router)


@app.get("/", tags=["Health"])
async def root():
    """Endpoint de salud de la API"""
    return {
        "status": "ok",
        "service": settings.app_title,
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
