from google import genai
from langchain_core.embeddings import Embeddings

class GeminiEmbeddings(Embeddings):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        results = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts
        )

        embeddings = [item.values for item in results.embeddings]
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        results = self.client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return results.embeddings[0].values
