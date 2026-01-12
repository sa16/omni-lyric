import time
from typing import List
from sqlalchemy.sql import select
from sqlalchemy.dialects.postgresql import insert
from src.db.session import SessionLocal
from src.ml.embeddings import embedding_model
from src.db.models import Track, TrackEmbedding

BATCH_SIZE = 200 # number of rows

def get_tracks_without_embedding(db, limit: int = BATCH_SIZE):
    subquery = select(TrackEmbedding.track_id).where(
        TrackEmbedding.model_version == embedding_model.MODEL_ID
    )

    query = select(Track).where(Track.id.not_in(subquery)).limit(limit)
    result = db.execute(query)
    
    return result.scalars().all() # returns list of sql alchemy orm objects

def save_embeddings(db, tracks: List[Track], vectors)-> int:

    """
    UPSERTS the generated vectors into the Embeddings table. 
    """
    embeddings_data=[]

    for i, track in enumerate(tracks):
        embeddings_data.append({
            "track_id": track.id,
            "embedding": vectors[i].tolist(),
            "model_version": embedding_model.MODEL_ID

        })

    if not embeddings_data:
        return 0

    stmt = insert(TrackEmbedding).values(embeddings_data)

    stmt = stmt.on_conflict_do_nothing(
        index_elements=['track_id', 'model_version']
    )

    result = db.execute(stmt)
    db.commit()

    return result.rowcount

def run_pipeline():

    print("starting emdedding process..")

    total_processed =0

    while True:
        db= SessionLocal()
        try:
            #Fetch batch of tracks
            tracks = get_tracks_without_embedding(db, BATCH_SIZE)

            if not tracks:
                print("All tracks have been processed, no missing embeddings")
                break
            
            items = [
               
               
               {
                    "title" : t.title,
                    "artist": t.artist,
                    "lyrics": t.lyrics,

                    
                }
                for t in tracks
                
                ]

            #generate embeddings
            #measure time to gauge/track performance metrics

            t0 = time.time() #start time
            vectors = embedding_model.generate(items, batch_size=32)
            duration = time.time() - t0 
        
            #save embeddings to db
            saved_count = save_embeddings(db, tracks, vectors)
            total_processed +=saved_count
            rate = len(tracks)/(duration+0.0001) # adding 0.0001 to avoid division by 0
        
            print(f'Saved {saved_count} vectors. (speed : {rate: .1f} song/sec)  | total saved : {total_processed}')
        
        except Exception as e:
            print(f'pipeline failed {e}')
            db.rollback()
            break
    
        finally:  
            db.close()
        
if __name__ == "__main__":
    run_pipeline()




        








        

