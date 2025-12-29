from typing import List, Dict, Any
from src.db.session import SessionLocal
from sqlalchemy.orm import Session
from src.db.models import Track

class DataLoader():
    def __init__(self, db: Session):
        self.db=db

    def load_tracks(self, raw_data: List[Dict[str, Any]]) -> int:

        tracks_to_insert=[]

        for item in raw_data:
            if not item.get("title") or not item.get("artist"):
                print(f'⚠️Skipping invalid row: {item}')
                continue

            track = Track(
                title = item['title'],
                artist = item['artist'],
                album = item.get('album'),
                release_year = item.get('release_year'),
                lyrics = item.get('lyrics'),
                genre= item.get('genre'),
                popularity_score = item.get('popularity_score', 0.0)



            )

            tracks_to_insert.append(track)

        if not tracks_to_insert:
            return 0
        
        try:
            self.db.bulk_save_objects(tracks_to_insert)
            self.db.commit()
            print(f'Succesfully committed {len(tracks_to_insert)} tracks')
            return len(tracks_to_insert)
        
        except Exception as e:
            self.db.rollback()
            print(f'Batch insert failed: {e}')
            return 0
        

def ingest_batch(data: List[Dict[str, Any]]):
    db = SessionLocal()

    try:
        loader= DataLoader(db)
        loader.load_tracks(data)

    finally:
        db.close()
        

    
    

    
                 




