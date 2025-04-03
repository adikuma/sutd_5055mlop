import os
import json
import openai
import faiss
import numpy as np
from typing import List, Dict, Union, Tuple
from sentence_transformers import SentenceTransformer

# ========= SETUP =========
openai.api_key = "insert key here"

MODELS_TO_COMPARE = ["text-embedding-ada-002"]
# TESTED MODELS = ["text-embedding-3-small", "text-embedding-ada-002", "sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2"]

# ========= EMBEDDINGS =========
def get_embeddings(
    data: Union[List[str], List[Dict]],
    model: str = "text-embedding-ada-002"
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Get embeddings for a list of plain strings or dicts with 'text' and 'metadata'.
    Returns:
        - np.ndarray of shape (n, dim)
        - List of metadata dicts (or empty dicts if strings)
    """
    
    if isinstance(data[0], str):
        texts = data
        metadata = [{} for _ in texts]
    elif isinstance(data[0], dict) and "text" in data[0]:
        texts = [item["text"] for item in data]
        metadata = [item.get("metadata", {}) | {"text": item["text"]} for item in data]
    else:
        raise ValueError("Input must be list of strings or list of dicts with 'text' and 'metadata'.")

    print(f"\nEmbedding {len(texts)} items with model: {model}")

    # Handle Both OpenAI and Hugging Face Model Instances
    if model.startswith("text-embedding-"):
        response = openai.embeddings.create(model=model, input=texts)
        embeddings = np.array([r.embedding for r in response.data]).astype("float32")
    else:
        hf_model = SentenceTransformer(model)
        embeddings = hf_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True).astype("float32")

    return embeddings, metadata

# ========= FAISS =========
def create_faiss_index(embeddings: np.ndarray) -> faiss.IndexFlatL2:
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    return index

def query_faiss_index(
    query: str,
    model: str,
    index: faiss.IndexFlatL2,
    metadata: List[Dict],
    k: int = 3
) -> List[Tuple[int, float, Dict]]:
    query_embedding, _ = get_embeddings([query], model)
    distances, indices = index.search(query_embedding, k)
    results = []

    for i, dist in zip(indices[0], distances[0]):
        results.append((i, dist, metadata[i]))

    return results

# ========= OUTPUT RESULTS =========
def print_top_k(results: List[Tuple[int, float, Dict]], model: str):
    print(f"\nTop {len(results)} Results for Model: {model}")

    for rank, (i, dist, meta) in enumerate(results, 1):
        print(f"\nRank {rank} (Distance: {dist:.4f})")
        print(f"Title: {meta.get('title', 'N/A')}")
        print(f"URL: {meta.get('url', 'N/A')}")
        print(f"Text: {meta.get('text', '')[:250]}...")

# ========= MAIN PIPELINE =========
with open("processed_sutd_chunks.json", "r") as f:
    input_data = json.load(f)

query = "What scholarships and financial aid are available for undergraduate students?"

for model in MODELS_TO_COMPARE:
    embeddings, metadata = get_embeddings(input_data, model)
    faiss_index = create_faiss_index(embeddings)

    results = query_faiss_index(query, model, faiss_index, metadata, k=3)

    print_top_k(results, model)
