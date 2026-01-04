from typing import List, Dict, Any
from src.db.session import SessionLocal
from sqlalchemy.orm import Session
from src.db.models import Track
from sqlalchemy.dialects.postgresql import insert

class DataLoader():
    def __init__(self, db: Session):
        self.db=db

    def load_tracks(self, raw_data: List[Dict[str, Any]]) -> int:

        if not raw_data:
            return 0

        tracks_to_insert=[]

        for item in raw_data:
            if not item.get("title") or not item.get("artist"):
                print(f'⚠️Skipping invalid row: {item}')
                continue

            track_dict = {
                "title" : item['title'],
                "artist" : item['artist'],
                "album" : item.get('album'),
                "release_year" : item.get('release_year'),
                "lyrics" : item.get('lyrics'),
                "genre" :item.get('genre'),
                "popularity_score" : item.get('popularity_score', 0.0)



            }

            tracks_to_insert.append(track_dict)

        if not tracks_to_insert:
            return 0
        
        try:
            # self.db.bulk_save_objects(tracks_to_insert)
            # self.db.commit()
            #stmt - upsert stmt, either update or insert (if record doesn't exist)
            stmt = insert(Track).values(tracks_to_insert)

            stmt = stmt.on_conflict_do_nothing(
                index_elements=['title', 'artist']
            )
            result = self.db.execute(stmt)
            self.db.commit()
            print(f'Succesfully committed {result.rowcount} tracks')
            return result.rowcount  
        
        except Exception as e:
            self.db.rollback()
            print(f'Batch insert failed: {e}')
            return 0
        

def ingest_batch(data: List[Dict[str, Any]]):
    db = SessionLocal()

    try:
        loader= DataLoader(db)
        return loader.load_tracks(data)

    finally:
        db.close()
        

    
    

    
                 




