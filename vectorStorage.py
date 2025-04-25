import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict

embedder = SentenceTransformer("all-MiniLM-L6-v2")

class VectorStore:
    def __init__(self, persist_dir: str = "chroma"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(settings=Settings(persist_directory=persist_dir))
        self.collection = self.client.get_or_create_collection(name="history_chunks")

    def insert(self, chunks: List[str], metadata: List[Dict]):
        if len(chunks) != len(metadata):
            raise ValueError("Chunks and metadata must be the same length.")
        
        ids = [str(meta["chunkId"]) for meta in metadata]
        embeddings = embedder.encode(chunks).tolist()

        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadata
        )
        print(f"Inserted {len(chunks)} chunks into vector database.")

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        query_embedding = embedder.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        formatted = []
        for i in range(len(results["documents"][0])):
            formatted.append({
                "chunkId": results["metadatas"][0][i].get("chunkId"),
                "page": results["metadatas"][0][i].get("page"),
                "section": results["metadatas"][0][i].get("section"),
                "text": results["documents"][0][i],
                "score": results["distances"][0][i]
            })
        return formatted

    def delete(self, chunk_ids: List[int]):
        str_ids = [str(cid) for cid in chunk_ids]
        self.collection.delete(ids=str_ids)
        print(f"🗑️ Deleted chunks: {str_ids}")

    def update(self, chunk_id: int, new_text: str, metadata: Dict):
        embedding = embedder.encode([new_text]).tolist()
        self.collection.update(
            ids=[str(chunk_id)],
            documents=[new_text],
            embeddings=embedding,
            metadatas=[metadata]
        )
        print(f"Updated chunk {chunk_id}.")

    def reset(self):
        self.client.delete_collection("history_chunks")
        self.collection = self.client.get_or_create_collection(name="history_chunks")
        print("Reset vector store.")

