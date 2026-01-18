from src.db.session import SessionLocal
from src.ml.pipeline import get_tracks_without_embedding, save_embeddings
from src.ml.embeddings import embedding_model

def test_pipeline_integration():

    print("Starting pipeline integration smoke test.....")

    db = SessionLocal()

    try:
        #fetching a small batch of 5 tracks for integration testing. 

        tracks = get_tracks_without_embedding(db, limit= 5)

        if not tracks:
            print("0 tracks found to process, check if DB is empty")
            return
        
        print(f'fetched {len(tracks)} to process for smoke test.')


        # using the pipeline logic

        items = [{
            "title":t.title,
            "artist":t.artist,
            "lyrics":t.lyrics

        }
        for t in tracks
        ]

        #generate vectors to test embedding model & hardware

        vectors = embedding_model.generate(items, batch_size=5)

        print(f'generated vectors: {vectors.shape}')

        #test db write & on conflict logic
        saved_count = save_embeddings(db,tracks,vectors)

        print(f'tracks embedded & saved: {saved_count}')

        assert len(tracks) == saved_count, "Mis-match between fetched & loaded trackes!"
        print("SMOKE TEST PASSED !")

    except Exception as e: 
        print(f'smoke test failed {e}')
        db.rollback()
        raise

    finally: 
        db.close()

if __name__ == "__main__":
    test_pipeline_integration()












