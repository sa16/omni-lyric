## ![alt text](https://github.com/sa16/omni-lyric/blob/main/Frontend/src/assets/omnis.jpeg) OMNI SEARCH - Semantic Similarity Search & Retreival Engine 

![alt text](https://img.shields.io/badge/status-live-success?style=flat-square)

![alt text](https://img.shields.io/badge/python-3.12-blue?style=flat-square)

![alt text](https://img.shields.io/badge/stack-FastAPI_React_Postgres-orange?style=flat-square)

![alt text](https://img.shields.io/badge/container-dockerized-blue?style=flat-square)

🔗 Live Demo | 📄 API Documentation

This is not a traditional Keyword search engine (BM25). The underlying principle here is to use vector embedding to understand conceptual similarity, from the lyrics.

# Architecture:

![System Architecture](/Frontend/src/assets/architecture.svg)


## Tech Stack:

Backend: FastAPI (Python 3.12), Uvicorn.
ML Engine: sentence-transformers (HuggingFace), optimized for Apple Silicon (MPS) & CUDA.
Database: PostgreSQL 16 with pgvector extension.
Indexing: HNSW (Hierarchical Navigable Small World) for sub-50ms approximate nearest neighbor search.
Frontend: React, Vite, TailwindCSS.
Infrastructure: Docker (Containerization), Render (Backend Hosting), Supabase (Managed DB), Vercel (Frontend).

Microservice-style-monolith: Clear seperations of data, ingestion, inference, model logic & retreival layers.

# Engineering Features:

1. HNSW index O(logn )vs sequential scan (O(n)) - Implemented hnsw using pgvector & inner product (vector_ip_ops)

    -Latency: <300ms on 57K+ tracks
    -Math: Vectors are L2-normalized during inference, allowing us to use Inner Product as a proxy for Cosine Similarity for faster computation.

2. Idempotent Ingestion Pipleline: 

    -Schema Enforcement: Uses SQLAlchemy UniqueConstraints to prevent duplicate vectors.
    -Conflict Resolution: Implements ON CONFLICT DO NOTHING logic. The pipeline can crash and restart without data corruption or duplication.
    -Delta Loading: Logic explicitly checks for tracks without corresponding track_embeddings to avoid re-computing existing vectors.

3. REST API Design: 

    -Layered Architecture: Strict isolotion between Controllers (routes.py), Services (search.py), and Contracts (schemas.py).
    -Dependency Injection: Database sessions are managed via FastAPI Depends(), ensuring proper connection pooling and teardown.
    -Lifecycle Management: embedding model is loaded into memory once on server startup (lifespan), preventing the "Cold Start" penalty on individual requests.
    -Dependency Pinning: Solved the NumPy 2.0 / PyTorch binary incompatibility by strictly locking dependency versions in pyproject.toml.


Local dev setup guide: 

Pre-reqs: docker, docker compose, python: ^3.12, poetry

1. Infra:

$ docker compose --env-file .env -f docker/docker-compose.yml up -d

2. Initialize schema & data:

    -Apply Schema
    $ poetry run python -m src.db.init_db

    -Ingest Dummy Data (Smoke Test)
    $ poetry run python -m src.ingestion.test_ingest

3. API setup:
    $ poetry run uvicorn src.api.app:app --reload

test using swagger UI - http://localhost:8000/docs

# Design tradeoffs: 

postgres + pgvector for vector storage & index VS a managed pector store (eg. Pinecone) - chose a unified architecture where Metadata and Vectors live in the same ACID-compliant database, whil specialized Vector DBs (Pinecone) offer scale, they introduce the "Dual-Write Problem" (keeping metadata in sync with vectors). For a dataset of ~1M rows, Postgres offers sufficient performance with significantly less operational complexity. Less computation intensive on the RAM. 

Batch ingestion for V1 vs Streaming data (& making it more upto date) - The ingestion pipeline processes data in batches of 200, generating embeddings is compute-bound (GPU/CPU), while writing to DB is I/O bound. Batching allows us to amortize the network overhead of database transactions while maximizing GPU throughput during inference. Besides, batch ingestion helped solve cold start & backfill problems. Alternatively, hitting an api for 60k tracks was not feasible. 

# Future versions:

Hybrid Search: Implement Reciprocal Rank Fusion (RRF) to combine Vector Similarity with Keyword Search (BM25) to fix Named Entity recognition (e.g., searching for specific artists).
Re-Ranking: Add a Cross-Encoder step (using ms-marco-MiniLM) to re-rank the top 20 results for higher precision.
Live Indexing: Implement a CDC (Change Data Capture) pipeline to automatically vectorise new songs added to the metadata table.
toggle to search based on music vs lyrics: Right now semantic similarity is based on lyrics, future versions will have genre based matching option.
hybrid ingestion: Will add streaming data pipelines to ensure dataset is upto date with latest tracks, pop culture relevant. 






