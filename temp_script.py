import chromadb
from chromadb.config import Settings
from llm_question import query_model



client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory="./chromadb_data"))
collection = client.get_or_create_collection(name="pdf_content")

text_chunks = processed_text.split(". ")  # Example of simple sentence-based chunking

for i, chunk in enumerate(text_chunks):
    embedding = generate_embedding(chunk)
    collection.add(
        documents=[chunk],
        embeddings=[embedding],
        metadatas=[{"source": "reddit_posts_with_comments.pdf"}],
        ids=[f"chunk_{i}"]
    )

