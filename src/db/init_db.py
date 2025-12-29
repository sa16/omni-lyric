from sqlalchemy import text
from src.db.session import engine, Base
from src.db.models import Track, TrackEmbedding

def init_db(): 
    print(f'connecting to {engine.url}....')

    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            print("Vector extension enabled ✅")

        Base.metadata.create_all(bind=engine)
        print("tables created succesfully ✅")

    except Exception as e:
        print(f'initialization failed{e} ❌')


if __name__ == "__main__": 
    init_db()



