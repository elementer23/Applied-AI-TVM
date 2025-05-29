# rag.py
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from tvm.models import AdvisoryText
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")
docs = []
vectors = []
index = None

def build_index(db: Session):
    global index, docs, vectors

    advisory_rows = db.query(AdvisoryText).all()
    docs = [
        f"Category: {row.category.name}\nSubcategory: {row.sub_category.name}\nText: {row.text}"
        for row in advisory_rows
    ]
    vectors = model.encode(docs)
    index = faiss.IndexFlatL2(vectors[0].shape[0])
    index.add(np.array(vectors))

def search_advisory(query: str, k: int = 3):
    query_vec = model.encode([query])
    D, I = index.search(np.array(query_vec), k)
    return [docs[i] for i in I[0]]
