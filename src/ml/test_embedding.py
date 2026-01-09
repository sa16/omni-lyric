import numpy as np
from src.ml.embeddings import embedding_model

def test_generation():
    print("starting embedding test.....")

    #dummy data
    dummy_tracks= [
        {
            'title':'Test Song',
            'artist':'Test Artist',
            'lyrics':'This is happy song about coding'

        },
        {
            'title':'Sad Song',
            'artist':'Blue Artist',
            'lyrics':'This is sad song about debugging'
        },
        
    ]

    #generate embeddings

    vectors = embedding_model.generate(dummy_tracks, batch_size=2)

    #validation
    print(f'Output Shape: {vectors.shape}')

    assert vectors.shape[0]==2, "Should have 2 vectors"
    assert vectors.shape[1]==384, "Should be 384 dimensions"

    #semantic sanity check - using dot product
    #vectors are already normalized
    #test song & happy song should be different from sad song...

    similarity = np.dot(vectors[0],vectors[1])

    print(f'similarity between happy & sad song: {similarity: .4f}')

    print("embedding model has passed sanity check!")

if __name__ == "__main__":
    test_generation()


