import logging
import threading
from typing import List, Dict, Any, Optional
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:

    """
    reusable componenet for Sentence Transformer, hardware-accelarator, input-formating, embedding.
    """

    #config, pinned to version, to restrict drifts & index breaking post huggingface updates. 
    #MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
    MODEL_ID = "all-MiniLM-L6-v2"
    MODEL_REVISION = "fa97f6e7cb1a59073dff9e6b13e27730ea7d508f"
    EXPECTED_DIM = 384
    MAX_SEQ_LENGTH = 256 #limit specific to model




    def __init__(self):
        self._lock= threading.Lock() #to prevent race condition, during high cuccurency 
        self.device = self._get_device() # _get_device() returns hardware name, expecting either cuda, mps or cpu.

        logger.info(f'Loading Embedding Model on {self.device}')

        try:
            self.model = SentenceTransformer(self.MODEL_ID, device = self.device)
            self.model.max_seq_length = self.MAX_SEQ_LENGTH

            actual_dim = self.model.get_sentence_embedding_dimension()

            if actual_dim != self.EXPECTED_DIM:
                raise ValueError(f'!Model Dimensions mismatch. Expected {self.EXPECTED_DIM} got {actual_dim}')
            
            logger.info(f"Succesfully loaded embedding model: {self.MODEL_ID}")

        except Exception as e:
            logger.error(f'failed to load embedding model{e}')
            raise  #should change to raise from raise e
        
    def _get_device(self)->str:
        """
        determines the best available hardware to run embedding model . PRIORITY: NVIDIA Cuda > MPS (Apple Silicon) > CPU

        """

        if torch.cuda.is_available(): 
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
        
    def _create_contextual_text(self, title: str, artist: str, lyrics: str)->str:
        """
        construct a structured string for the model. With the following format: title: {t} | artist: {a} | lyrics: {l} 
        a labeled & structered adds more context to input & helps with semantic understanding, compared to raw string: "{title}, {artist}, {lyrics}"

        """

        #the seq length limit for the model is set at 256, hence the lyrics would have to be truncated slightly to accomadate for artist & title fields
        clean_lyrics = (lyrics or "").replace("\n"," ").strip()[:1000]
        
        return f'Title: {title} | Artist: {artist} | Lyrics: {clean_lyrics}'

    def generate(self, items: List[Dict[str, Any]], batch_size: int = 32)-> np.ndarray:
        """
        batch_size default is 32, however, stating it explicitly as model may alter batch_size during traffic spikes, hard set defautl
        will help protect MPS/CPU memory from cache thrashing, OOM. Also prevent latency  & throughput drops.
        """

        #creating structered string
        text_batch=[
            
                self._create_contextual_text(
                    title = item.get('title', "unknown"),
                    artist = item.get('artist', "unknown"),
                    lyrics = item.get('lyrics', "")
                )
                for item in items
        ]
        #ensuring isolation, no concurrent encoding
        #normalized since we are using dot product over cosine similarity (faster in postgres)
        with self._lock:
            embeddings=self.model.encode(
                text_batch, 
                batch_size=batch_size, 
                normalize_embeddings= True,
                show_progress_bar = False,
                convert_to_numpy= True
            )
        return embeddings
    
embedding_model = EmbeddingModel()
        



    

    

