import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

class QdrantHandler:
    def __init__(self, collection_name="nepal_constitution_v1"):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = collection_name
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vector_size = 384

    def create_collection(self):
        if not self.client.collection_exists(self.collection_name):
            print(f"🔨 Creating Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE)
            )

    def store_data(self, chunks):
        self.create_collection()
        print(f"💾 Generating embeddings for {len(chunks)} chunks...")

        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        points = []

        for i, chunk in enumerate(chunks):
            text_content = chunk['text']
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, text_content))

            payload = {"text": text_content, **chunk['metadata']}

            points.append(PointStruct(
                id=point_id,
                vector=embeddings[i].tolist(),
                payload=payload
            ))

        self.client.upsert(collection_name=self.collection_name, points=points)
        print(f"🚀 Success! {len(points)} chunks stored/updated in Qdrant.")

    def search(self, query_text, top_k=3):
        """Search using Qdrant's query_points API."""
        query_vector = self.model.encode(query_text).tolist()

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        )

        return results.points
