import uuid
from sqlalchemy import Column, String, Float, Integer, Text, String, DateTime, ForeignKey, func
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import UUID
from src.db.session import Base


class Track(Base):

    __tablename__ = "tracks"

    #Primary key - id

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


     #metadate/schema

    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    release_year = Column(Integer, nullable=True)
    lyrics = Column(Text, nullable=True)
    popularity_score = Column(Float, default=0.0)

    #for audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class TrackEmbedding(Base):

    __tablename__ = "track_embeddings"

    id= Column(Integer, primary_key=True, index=True) 


    #foreign key, CASCADE deletes entry if deleted in other table
    track_id = Column(UUID(as_uuid=True), ForeignKey("tracks.id", ondelete="CASCADE"), nullable=False)

    embedding = Column(Vector(384)) #dimensional space to meet v1_minilm requirement.

    #model versioning provisions for A/B testing in subsequent stages.
    model_version = Column(String, default="v1_minilm")


    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


