from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router
from src.ml.embeddings import embedding_model
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup & shutdown events
    crucial for loading heavy ML models into RAM before traffic hits 

    """

    #warm-up: dummy inferance, to get weights occupied into mps/cuda

    try:
        logger.info(f'API Starting Loading MODEL: {embedding_model.MODEL_ID}')
        embedding_model.generate([{"title": "warm-up", "artist":"warm-up","lyrics":"warm-up"}])

        logger.info("Model succesfully loaded & ready on device.")
        

    except Exception as e:
        logger.error(f'CRITICAL: MODEL FAILED TO LOAD {e}')
        raise

    yield

    logger.info("API shutting down.")

app = FastAPI(
    title="Music retrieval Api",
    version= '1.0.0',
    description="semantic search engine powered by PGVECTOR & SentenceTransformers",
    lifespan=lifespan

)

#registering the routes 
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    """
    kubernetes/Docker health check point

    """
    return {
        "status":"healthy",
        "model": embedding_model.MODEL_ID,
        "device": embedding_model.device
    }
