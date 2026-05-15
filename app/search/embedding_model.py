import numpy as np
from threading import Lock

_model = None
_model_lock = Lock()

def load_model(
    # model_name: str = "Snowflake/snowflake-arctic-embed-s", # 384 vector len
    # model_name: str = "sentence-transformers/all-mpnet-base-v2", # 768 vector len
    model_name: str = "BAAI/bge-base-en-v1.5", # ? vector len
    cache_dir: str = "./models", 
    download: bool = False
):
    from sentence_transformers import SentenceTransformer
    global _model
    # Thread-safe check
    with _model_lock:
        if _model is not None:
            return _model
        _model = SentenceTransformer(model_name, cache_folder=cache_dir, local_files_only=not download)
    return _model 


# def get_embed_dim():
#         return embed_model.encode("")

def embed_text(text: str) -> np.ndarray:
    model = load_model()
    emb = model.encode(text, normalize_embeddings=True)
    return np.array(emb, dtype=np.float32)


def embed_batch(texts: list[str]) -> np.ndarray:
    model = load_model()
    embs = model.encode(texts, normalize_embeddings=True)
    return np.array(embs, dtype=np.float32)


if __name__ == "__main__":
    load_model(download=True)
    # import os
    # print(os.path.abspath("./models"))