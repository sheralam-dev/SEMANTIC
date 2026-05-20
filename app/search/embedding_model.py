import os
import numpy as np
from threading import Lock
from  torch import cuda

from app.utils.paths import MODEL_PATH, BASE_DIR

_model = None
_model_lock = Lock()


def load_model(
    model_name: str = "Snowflake/snowflake-arctic-embed-s",
    cache_dir: str = str(MODEL_PATH), 
    download: bool = True
):
    from sentence_transformers import SentenceTransformer
    global _model
    device = "cuda" if cuda.is_available() else "cpu"
    
    # Format the name exactly like Hugging Face does for the folder
    repo_id = model_name.replace("/", "--")
    folder_name = f"models--{repo_id}"
    full_path = os.path.join(cache_dir, folder_name)

    with _model_lock:
        if _model is not None:
            return _model
            
        print(f"Checking Path: {full_path}")
        
        # If the HF folder exists, load from the cache_dir
        if os.path.exists(full_path):
            print("Model found in cache. Loading locally...")
            _model = SentenceTransformer(
                model_name, 
                cache_folder=cache_dir, 
                local_files_only=True
            ).to(device)
        else:
            if not download:
                raise FileNotFoundError(f"Model not found and download=False")
            print("Downloading model...")
            _model = SentenceTransformer(model_name, cache_folder=cache_dir).to(device)
            
    return _model


def embed_text(text: str) -> np.ndarray:
    model = load_model()
    emb = model.encode(text, normalize_embeddings=True)
    return np.array(emb, dtype=np.float32)


def embed_query(query: str):
    model = load_model()
    return model.encode_query(query)


def embed_batch(texts: list[str]) -> np.ndarray:
    model = load_model()
    batch_size = 256 if model.device == "cuda" else 32
    embs = model.encode(texts, batch_size=batch_size, show_progress_bar=False, normalize_embeddings=True)
    return np.array(embs, dtype=np.float32)


def embed_documents(descriptions: list[str]):
    model = load_model()
    return model.encode_document(
        descriptions, 
        batch_size=32, 
        show_progress_bar=False
    )


if __name__ == "__main__":
    m = load_model(download=False)
    print(m.get_embedding_dimension())
    # import os
    # print(os.path.abspath("./models"))