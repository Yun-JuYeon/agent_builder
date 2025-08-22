from pathlib import Path
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.db.pgvector import get_vectorstore
from app.core.embedding import GeminiEmbeddings
from app.config import settings

embedding_client = GeminiEmbeddings(settings.GOOGLE_API_KEY)


# 1. PDF 읽기
def get_pdf(file_path: str):
    file_stem = Path(file_path).stem
    loader = PyMuPDFLoader(file_path)
    docs = loader.load()
    # print(f"sample_content: {docs[5].page_content[:300]}")
    # print(f"sample_metadata: {docs[5].metadata}")

    # 2. 청크 분리
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunked_docs = splitter.split_documents(docs)

    vectorstore = get_vectorstore(collection_name=file_stem)
    existing_docs = vectorstore.similarity_search("test", k=1)
    if existing_docs:  # 뭔가 이미 들어있으면
        print(f"⚡ 이미 컬렉션({file_stem})이 존재합니다. 임베딩 건너뜀.")
        return vectorstore
    
    # 3. 임베딩 & PGVector에 저장
    texts = [d.page_content for d in chunked_docs]
    metadatas = [d.metadata for d in chunked_docs]
    vectorstore.add_texts(texts=texts, metadatas=metadatas)

    print("✅ PDF 임베딩 & 저장 완료")

    return vectorstore


def search_similar(query: str, file_path: str, top_k: int = 5):
    embedded_query = embedding_client.embed_query(text=query)

    vectorstore = get_pdf(file_path=file_path)
    results = vectorstore.similarity_search_by_vector(embedding=embedded_query, k=top_k)

    for tmp_result in results:
        tmp_source = tmp_result.metadata["source"]
        tmp_page = tmp_result.metadata["page"]
        tmp_content = tmp_result.page_content

        print(f"[CONTENT]: {tmp_content}")
        print(f"[METADATA - SOURCE]: {tmp_source}")
        print(f"[METADATA - PAGE]: {tmp_page}")

    return results


if __name__ == "__main__":
    file_path = "app/data/SPRI_AI_Brief_2023년12월호_F.pdf"
    search_result = search_similar(query="AI정책연구실", file_path=file_path, top_k=10)
