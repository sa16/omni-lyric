from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional

# REQUESTS - INPUT rules & contracts

class SearchRequest(BaseModel):
    query: str = Field(...,min_length=3, description="The search text (eg: Kendrick Lamar track about being better than everyone..)")
    limit: int = Field(10, ge=1, le=50, description="Max results to return")

    # ... -> parameter is to ensure no blank inputs are accepted.

# RESPONSE - Metadata

class TrackMetadata(BaseModel):
    title: str
    artist: str
    album: Optional[str] = None
    release_year: Optional[str] = None

class SearchResult(BaseModel):
    id: UUID
    score: float = Field(..., description="Cosine Similiarity [0,1], higher the better")
    metadata: TrackMetadata

class SearchResponse(BaseModel):
    results: List[SearchResult]
    latency_ms: float
    model_version: str = Field(..., description="Embedding Model used")