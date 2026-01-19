from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api.routes import router
from src.ml.embeddings import embedding_model
import logging
import httpx
from fastapi.middleware.cors import CORSMiddleware
import os

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

    #shared http client
    app.state.http_client = httpx.AsyncClient(timeout=httpx.Timeout(5.0,connect=2.0, read=3.0)) #fail fast in case of failure
    logger.info("http client initialized.")


    yield

    #shutdown

    logger.info("API shutting down.")

    #cleanup http client
    await app.state.http_client.aclose()

   

app = FastAPI(
    title="Music retrieval Api",
    version= '1.0.0',
    description="semantic search engine powered by PGVECTOR & SentenceTransformers",
    lifespan=lifespan

)

 #CORS middleware (crucial for vercel/render communication)
 # SECURITY: In production, this should be set to "https://your-frontend.vercel.app"
# Default to "*" for local development convenience.

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS","*").split(",")
app.add_middleware(
    CORSMiddleware, 
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
     allow_headers=["*"],
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
