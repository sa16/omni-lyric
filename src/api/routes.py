import time
import logging
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.ml.embeddings import embedding_model
from src.api.schemas import SearchRequest, SearchResponse
from src.api.services.search import SearchService
from fastapi import APIRouter, Depends, HTTPException, Query, Request
import httpx

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
    
#new proxy route
@router.get('/proxy/itunes')
async def proxy_itunes(
    request: Request,
    term: str = Query(..., min_length=1, description="Song title or artist"),
    limit: int = 1
    ):

    """
    Proxy end point to fetch audio previews from itunes (chose itunes, due to easier implementation compared to spotify)

    """
    
    """
    #SECURITY NOTE:
    This endpoint is currently public to allow for easy demo access.
    In a production environment, this should be protected by:
    1. Rate Limiting (e.g. 10 req/min per IP) via Redis/SlowAPI.
    2. Origin Validation (CORS is configured in app.py).
    3. Caching (e.g. HTTP headers or server-side cache) to reduce upstream calls.
    
    """
    #input guardrails & safe limit to prevent request abuse
    if not term.strip():
        raise HTTPException(status_code=400,detail="seach term cannot be empty")
    
    safe_limit = min(limit, 5)
    itunes_url = "https://itunes.apple.com/search"

    #params expected by apple.com
    params = {
        "term": term,
        "media": "music",
        "entity":"song",
        "limit":safe_limit
    }

    # async with httpx.AsyncClient() as client:
    client: httpx.AsyncClient = request.app.state.http_client

    try: 
            logger.debug(f'Proxying request to iTunes for term: {term}')
            response = await client.get(itunes_url, params=params,timeout=5.0)
            response.raise_for_status()

            return response.json()
        
    except httpx.HTTPStatusError as e:
            logger.error(f'itunes api error: {e.response.status_code} - {e.response.text}')
            raise HTTPException(status_code=e.response.status_code, detail="upstream provide error")
        
    except Exception as e:
            logger.error(f'itunes proxy failed : {e}')
            raise HTTPException(status_code=500, detail='failed to fetch preview')


