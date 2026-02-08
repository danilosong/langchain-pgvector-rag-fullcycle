import os
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_CONNECTION = os.getenv("POSTGRES_CONNECTION", f"postgresql+psycopg://langchain:langchain@{DB_HOST}:5432/langchain")
COLLECTION_NAME = "documents"

def get_embeddings():
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif os.getenv("GOOGLE_API_KEY"):
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    else:
        raise ValueError("No API key found via OPENAI_API_KEY or GOOGLE_API_KEY")

def get_vectorstore():
    embeddings = get_embeddings()
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )

def search(query: str, k: int = 10):
    """
    Performs a similarity search on the vector store.
    Returns a list of tuples (Document, score).
    """
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(query, k=k)
    return results
