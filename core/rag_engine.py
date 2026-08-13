import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

class MeetingRAG:
    def __init__(self, collection_name: str = "meetings"):
        self.client = chromadb.Client()
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_fn
            )
    
    def add_meeting(self, meeting_id: str, transcript: str, metadata: Dict[str, Any]):
        # Chunk transcript into ~500 word chunks
        words = transcript.split()
        chunks = []
        for i in range(0, len(words), 500):
            chunk = " ".join(words[i:i+500])
            if chunk.strip():
                chunks.append(chunk)
        
        for i, chunk in enumerate(chunks):
            self.collection.add(
                documents=[chunk],
                metadatas=[{"meeting_id": meeting_id, "chunk_index": i, **metadata}],
                ids=[f"{meeting_id}_chunk_{i}"]
            )
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return [
            {"content": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def get_all_meetings(self) -> List[str]:
        try:
            results = self.collection.get()
            meeting_ids = set()
            for meta in results["metadatas"]:
                if meta.get("meeting_id"):
                    meeting_ids.add(meta["meeting_id"])
            return list(meeting_ids)
        except:
            return []
    
    def delete_meeting(self, meeting_id: str) -> bool:
        try:
            results = self.collection.get(where={"meeting_id": meeting_id})
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
            return True
        except:
            return False
