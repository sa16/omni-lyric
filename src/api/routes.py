import time
import logging
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.ml.embeddings import embedding_model
from src.api.schemas import SearchRequest, SearchResponse
from src.api.services.search import SearchService
from fastapi import APIRouter, Depends, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post('/search', response_model=SearchResponse)
def search_tracks(request: SearchRequest, db: Session = Depends(get_db)):
    """
    Semantic Search end-point.
    Orchestration: Input Validation -> Vectorization -> DB Retrieval -> Response Formatting

    """

    t0 = time.time()

    try:

        service = SearchService(db)

        results = service.search(query = request.query, limit=request.limit)

        latency = (time.time() - t0 )* 1000

        return SearchResponse(results=results, latency_ms=round(latency,2),model_version=embedding_model.MODEL_ID)
    
    except ValueError as e:
        #catch known logic errors (eg: bad math, invalid input)
        logger.warning(f'Bad Request Logic: {e}')
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:

        logger.exception("Unexpected error during search execution.")
        raise HTTPException(status_code=500, detail=f'Internal search error.')

