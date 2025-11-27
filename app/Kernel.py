import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.config.setting import settings
from app.router.api.v1 import router as api_router
from app.config.qdrant import QdrantDB

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):    
    # 1. Initialize Database/Services on startup
    qdrant_db = QdrantDB()
    if qdrant_db.is_available():
        # Ensure collection exists on startup to avoid first-request latency
        qdrant_db.create_collection(settings.QDRANT_COLLECTION_NAME)
    else:
        logger.warning("Qdrant unreachable. System will run in In-Memory Fallback mode.")

    # (Optional) Place for other inits: Redis, Scheduler, etc.
    
    yield
    
    logger.info("Shutting down application...")
 

def create_app() -> FastAPI:
    """
    App Factory to create FastAPI instance with configurations.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan
    )

    # Register Routes
    app.include_router(api_router)

    return app

# Expose the app instance
app = create_app()