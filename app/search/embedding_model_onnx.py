import os
import numpy as np
from threading import Lock
import onnxruntime as ort
from tokenizers import Tokenizer

from app.utils.paths import MODEL_PATH

_model = None
_tokenizer = None
_model_lock = Lock()

def load_model(
    model_name: str = "Snowflake/snowflake-arctic-embed-s-onnx-int8",
    cache_dir: str = str(MODEL_PATH)
):
    global _model, _tokenizer
    
    # Mirroring your folder-naming system
    repo_id = model_name.replace("/", "--")
    folder_name = f"models--{repo_id}"
    full_path = os.path.join(cache_dir, folder_name)

    with _model_lock:
        if _model is not None and _tokenizer is not None:
            return _model, _tokenizer

        # Path configurations for ONNX components
        onnx_path = os.path.join(full_path, "model_quantized.onnx")
        tokenizer_path = os.path.join(full_path, "tokenizer.json")

        if not os.path.exists(onnx_path) or not os.path.exists(tokenizer_path):
            raise FileNotFoundError(
                f"ONNX files missing at {full_path}. Please download the repo folder."
            )

        print("Loading local ONNX model and fast tokenizer...")
        
        # Auto-detect CUDA vs CPU Execution Providers
        available_providers = ort.get_available_providers()
        provider = "CUDAExecutionProvider" if "CUDAExecutionProvider" in available_providers else "CPUExecutionProvider"
        
        # Load components completely independent of Torch
        _tokenizer = Tokenizer.from_file(tokenizer_path)
        _model = ort.InferenceSession(onnx_path, providers=[provider])
        
    return _model, _tokenizer


def _run_inference(texts: list[str]) -> np.ndarray:
    """Helper method to run the ONNX pipeline & apply Mean Pooling + Normalization."""
    session, tokenizer = load_model()
    
    # 1. Tokenize texts into numpy arrays directly
    tokenizer.enable_padding(direction="right", pad_id=0, pad_token="[PAD]")
    tokenizer.enable_truncation(max_length=512)
    
    encoded = tokenizer.encode_batch(texts)
    
    input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
    attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
    
    # Match the model graph's expected token type dimension if required
    token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

    # 2. Run ONNX Session inference
    ort_inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "token_type_ids": token_type_ids
    }
    ort_outputs = session.run(None, ort_inputs)
    
    # The first layer contains the token embeddings output matrix
    token_embeddings = ort_outputs[0] 

    # 3. Apply Mean Pooling to generate the global sentence embedding
    input_mask_expanded = np.expand_dims(attention_mask, axis=-1).astype(np.float32)
    sum_embeddings = np.sum(token_embeddings * input_mask_expanded, axis=1)
    sum_mask = np.clip(np.sum(input_mask_expanded, axis=1), a_min=1e-9, a_max=None)
    embeddings = sum_embeddings / sum_mask

    # 4. L2 Normalize output vectors
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    normalized_embeddings = embeddings / np.clip(norms, a_min=1e-9, a_max=None)
    
    return normalized_embeddings.astype(np.float32)


def embed_text(text: str) -> np.ndarray:
    # Standard sentence embedding utilizes no special prefix strings
    return _run_inference([text])[0]


def embed_query(query: str) -> np.ndarray:
    # Snowflake Arctic asymmetry prefix requirement for user queries
    prefixed_query = f"Represent recent query: {query}"
    return _run_inference([prefixed_query])[0]


def embed_batch(texts: list[str]) -> np.ndarray:
    return _run_inference(texts)


def embed_documents(descriptions: list[str]) -> np.ndarray:
    # Snowflake Arctic asymmetry prefix requirement for indexed documents
    prefixed_docs = [f"Represent recent document: {d}" for d in descriptions]
    return _run_inference(prefixed_docs)


if __name__ == "__main__":
    # Test execution
    emb = embed_query("What is ONNX Runtime?")
    print(f"Embedding successful! Dimensions: {emb.shape}")
