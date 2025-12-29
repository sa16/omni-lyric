from src.ingestion.loader import ingest_batch

def run_manual_test():
    dummy_data = [
        {
            "title": "Shape of You",
            "artist": "Ed Sheeran",
            "album": "Divide",
            "genre": "Pop",
            "release_year": 2017,
            "lyrics": "The club isn't the best place to find a lover...",
            "popularity_score": 0.95
        },
        {
            "title": "Bohemian Rhapsody",
            "artist": "Queen",
            "album": "A Night at the Opera",
            "genre": "Rock",
            "release_year": 1975,
            "lyrics": "Is this the real life? Is this just fantasy?...",
            "popularity_score": 0.99
        },
        {
            "title": "Blinding Lights",
            "artist": "The Weeknd",
            "release_year": 2020,
            # Missing album/genre/lyrics to test null handling
            "popularity_score": 0.92
        }
    ]
    
    print("Start test dummy data ingestion....")
    ingest_batch(dummy_data)
    print("dummy data ingested succesfully!")


if __name__ == "__main__": 
    run_manual_test()

