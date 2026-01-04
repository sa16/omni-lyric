import pandas as pd
import os 
import sys
from src.ingestion.loader import ingest_batch

CSV_PATH = "data/raw/spotify_millsongdata.csv"

COLUMN_MAPPING = {
    "song": "title",
    "artist": "artist",
    "text":"lyrics"
    #album
    #genre
    #popularity_score
}


def process_and_ingest(file_path: str, chunk_size: int = 1000):
    if not os.path.exists(file_path):
        print(f'{file_path} not found')
        sys.exit(1)

    print("starting ingestion...")
    chunk_iterator= pd.read_csv(file_path, chunksize=chunk_size, quotechar='"')
    total_ingested = 0

    for i, chunk in enumerate(chunk_iterator):
        chunk = chunk.rename(columns=COLUMN_MAPPING)

        #filling missing columns with defaults to handle cold-start

        if "album" not in chunk.columns:
            chunk["album"] = "Unknown-album"
        if "genre" not in chunk.columns: 
            chunk["genre"] = "unknown-genre"
        if "release_year" not in chunk.columns: 
            chunk["release_year"] = None
        if "popularity_score" not in chunk.columns: 
            chunk["popularity_score"] = 0.5


        valid_cols = ['title', 'artist', 'album', 'genre', 'release_year','lyrics','popularity_score']

        final_cols = [c for c in valid_cols if c in chunk.columns]

        chunk = chunk[final_cols]

        #converting to dictionary:

        batch_data = chunk.to_dict(orient="records")

        count = ingest_batch(batch_data)

        total_ingested += count

        print(f'batch {i+1} ingested. Total: {total_ingested}')

    print(f'Succesfully ingested {total_ingested} tracks.')

if __name__ == "__main__":
    process_and_ingest(CSV_PATH)


