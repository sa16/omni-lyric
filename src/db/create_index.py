from src.db.session import SessionLocal
import time
from sqlalchemy import text

def create_hnsw_index():
    db = SessionLocal()
    start_time = time.time()

    try:
        print('Building HNSW on track_embeddings.....')

        """
        index name: idx_track_embeddings_embedding
        method: hnsw, using inned product.
      
        """
        sql = text("""
                    CREATE INDEX IF NOT EXISTS idx_track_embeddings_embedding
                    ON track_embeddings
                    USING hnsw (embedding vector_ip_ops)
                    WITH (m=16, ef_construction=64);
                   """)
        #this is DDL (locked) operation
        db.execute(sql)
        db.commit()

        duration = time.time() - start_time

        print(f'index created succesfully in {duration:.2f} seconds.')

    except Exception as e:
        db.rollback()
        print(f'index creation failed {e}')

    finally:
        db.close()

if __name__ == "__main__":
    create_hnsw_index()
        


