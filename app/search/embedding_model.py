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
    
    with _model_lock:
        if _model is not None:
            return _model
        # 1. Join the paths and normalize for Windows
        # This converts forward slashes to backslashes and makes it absolute
        full_path = os.path.abspath(os.path.join(cache_dir, model_name))
        # 2. Add a sanity check print
        print(f"Checking Path: {full_path}")
        print(f"Folder exists: {os.path.exists(full_path)}")
        if os.path.exists(full_path):
            # Pass the absolute string path. Do NOT use model_name or cache_folder here.
            # Passing the full local path as the FIRST argument triggers offline mode.
            _model = SentenceTransformer(
                full_path, 
                local_files_only=True,
                trust_remote_code=True
            ).to(device)
        else:
            # Only if folder is missing, try downloading
            if not download:
                raise FileNotFoundError(f"Model not found at {full_path} and download=False")
            _model = SentenceTransformer(model_name).to(device)
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
    batch_size = 32 if model.device == "cuda" else 8
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