from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import print_router
from app.services.ip_service import IpService
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


settings = get_settings()
def _startup_update_local_ip():
    logger.info("Actualizando IP local en la BD")
    db_url = settings.resolved_database_url()
    logger.info(f"database_url: {db_url}")    
    res = IpService(database_url=db_url).update_ip_local()
    if res:
        logger.info("IP local actualizada en la BD")
    else:
        logger.error("IP no actualizada en la BD")
    
    
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


app.add_event_handler("startup", _startup_update_local_ip)


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
