from sqlalchemy.orm import Session
from typing import List
from src.api.schemas import TrackMetadata, SearchResult
from src.ml.embeddings import embedding_model
from sqlalchemy import select, Float
from src.db.models import Track, TrackEmbedding

class SearchService:

    def __init__(self, db: Session):
        self.db = db

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:

        """
        1. uses the embedding model to embed the query
        2. use inner product for ANN needed for HNSW search
        3. format result as per metadata contract
        4. retrieval post ANN compute & search 

        """

        vector = embedding_model.embed_query(query)

        distance_col = TrackEmbedding.embedding.op('<#>')(vector).cast(Float).label('distance') # <#> postgress negative inner product

        stmt= select(Track, distance_col).join(TrackEmbedding, Track.id == TrackEmbedding.track_id).order_by(distance_col.asc()).limit(limit)

        result = self.db.execute(stmt).all()

        # 5. Formating results
        response_items=[]

        for row in result:
            track = row[0] #Track ORM object
            neg_dot_prod = row[1] #row operator result
            similarity = -1* neg_dot_prod

            response_items.append(SearchResult(
                id=track.id,
                score = round(similarity,4), 
                metadata=TrackMetadata(
                    title=track.title,
                    artist=track.artist,
                    album=track.album,
                    release_year=track.release_year
                )))
            
        return response_items



        
