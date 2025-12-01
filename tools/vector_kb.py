# tools/vector_kb.py
# -------------------------------------------------------------
# FAISS Vector KB with Gemini Embeddings
# Debug prints added
# -------------------------------------------------------------

import os
import pickle
import numpy as np
import faiss

from typing import List
from google import genai
from google.adk.tools.function_tool import FunctionTool


FAISS_INDEX_PATH = "faiss_store.index"
DOCSTORE_PATH = "faiss_docstore.pkl"

client = genai.Client()

faiss_index = None
docstore = []


def load_vector_store():
    global faiss_index, docstore

    print("\n[TOOL:vector_kb] Loading vector store...")

    if os.path.exists(FAISS_INDEX_PATH):
        faiss_index = faiss.read_index(FAISS_INDEX_PATH)
        print("[TOOL:vector_kb] Loaded FAISS index.")
    else:
        faiss_index = None

    if os.path.exists(DOCSTORE_PATH):
        with open(DOCSTORE_PATH, "rb") as f:
            docstore[:] = pickle.load(f)
        print("[TOOL:vector_kb] Loaded docstore entries:", len(docstore))

    print("[TOOL:vector_kb] Ready.")


load_vector_store()


# -------------------------------------------------------------
# Embedding
# -------------------------------------------------------------
def embed_text(text: str) -> List[float]:
    print("\n[TOOL:vector_kb:embed] Embedding text...")
    resp = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
    )
    return list(resp.embeddings[0].values)


# -------------------------------------------------------------
# Add Document
# -------------------------------------------------------------
def add_kb_document(text: str, metadata: dict | None = None):
    print("\n[TOOL:vector_add] Adding document to FAISS...")
    global faiss_index, docstore

    try:
        embedding = embed_text(text)
        dim = len(embedding)

        if faiss_index is None:
            faiss_index = faiss.IndexFlatL2(dim)

        if faiss_index.d != dim:
            print("[TOOL:vector_add] Dimension mismatch → resetting index.")
            faiss_index = faiss.IndexFlatL2(dim)
            docstore.clear()

        vector = np.array(embedding, dtype="float32").reshape(1, -1)
        faiss_index.add(vector)

        docstore.append({"text": text, "metadata": metadata or {}})

        faiss.write_index(faiss_index, FAISS_INDEX_PATH)
        with open(DOCSTORE_PATH, "wb") as f:
            pickle.dump(docstore, f)

        print("[TOOL:vector_add] Document added.")
        return {"status": "success", "count": len(docstore)}

    except Exception as exc:
        print("[TOOL:vector_add] Error:", exc)
        return {"status": "error", "msg": str(exc)}


# -------------------------------------------------------------
# Search
# -------------------------------------------------------------
def vector_kb_search(query: str, top_k: int = 3):
    print("\n[TOOL:vector_search] Query:", query)
    global faiss_index, docstore

    if faiss_index is None or len(docstore) == 0:
        return {"status": "success", "results": [], "msg": "Vector store empty"}

    embedding = embed_text(query)
    q = np.array(embedding, dtype="float32").reshape(1, -1)

    distances, indices = faiss_index.search(q, top_k)

    results = []
    for score, idx in zip(distances[0], indices[0]):
        if 0 <= idx < len(docstore):
            results.append({
                "text": docstore[idx]["text"],
                "metadata": docstore[idx]["metadata"],
                "score": float(score),
            })

    print("[TOOL:vector_search] Found:", len(results))
    return {"status": "success", "results": results}


# -------------------------------------------------------------
# Wrap tools
# -------------------------------------------------------------
add_kb_document_tool = FunctionTool(
    lambda text, metadata=None, tool_context=None: add_kb_document(text, metadata)
)
vector_search_tool = FunctionTool(
    lambda query, tool_context=None: vector_kb_search(query)
)

__all__ = [
    "add_kb_document_tool",
    "vector_search_tool",
    "add_kb_document",
    "vector_kb_search",
]
