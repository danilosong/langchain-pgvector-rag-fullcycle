import os
import psycopg
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector
from dotenv import load_dotenv

load_dotenv()

# Configuration
# Use 'db' as host when running inside docker-compose, or 'localhost' if running locally
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_CONNECTION = os.getenv("POSTGRES_CONNECTION", f"postgresql+psycopg://langchain:langchain@{DB_HOST}:5432/langchain")
COLLECTION_NAME = "documents"

def ensure_vector_extension():
    """Ensures the vector extension exists in the database."""
    try:
        # Connect to default database to create extension if needed
        # Note: In a real production setup, this requires superuser or correct permissions
        conn = psycopg.connect(DB_CONNECTION)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            print("Extension 'vector' confirmed.")
        conn.close()
    except Exception as e:
        print(f"Warning: Could not enable vector extension automatically: {e}")
        print("Please ensure the 'vector' extension is enabled in the PostgreSQL database.")

def get_embeddings():
    if os.getenv("OPENAI_API_KEY"):
        print("Using OpenAI Embeddings")
        return OpenAIEmbeddings(model="text-embedding-3-small")
    elif os.getenv("GOOGLE_API_KEY"):
        print("Using Google Gemini Embeddings")
        return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    else:
        raise ValueError("No API key found via OPENAI_API_KEY or GOOGLE_API_KEY")

def ingest(file_path: str):
    ensure_vector_extension()
    
    print(f"Loading {file_path}...")
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(docs)
    print(f"Created {len(splits)} chunks.")

    print("Generating embeddings and storing in PGVector...")
    embeddings = get_embeddings()
    
    # Store documents
    PGVector.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        connection=DB_CONNECTION,
        use_jsonb=True,
    )
    print("Ingestion complete!")

if __name__ == "__main__":
    if not os.path.exists("document.pdf"):
        print("Error: document.pdf not found in current directory.")
    else:
        ingest("document.pdf")
