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
        # psycopg.connect expects 'postgresql://' not 'postgresql+psycopg://'
        start_u = DB_CONNECTION.replace("+psycopg", "")
        conn = psycopg.connect(start_u)
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
    try:
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
    except Exception as e:
        error_msg = str(e)
        # OpenAI Errors
        if "insufficient_quota" in error_msg or "429" in error_msg:
            print("\n" + "="*50)
            print("ERRO DE COTA (OPENAI/GEMINI):")
            print("Sua API Key está sem créditos ou excedeu o limite de requisições.")
            print("Solução: Verifique sua conta na OpenAI ou Google Cloud.")
            print("="*50 + "\n")
        # Gemini Errors (ResourceExhausted is common for free tier limits)
        elif "ResourceExhausted" in error_msg:
            print("\n" + "="*50)
            print("ERRO DE COTA (GEMINI):")
            print("Limite de requisições excedido (ResourceExhausted).")
            print("Solução: Aguarde alguns instantes ou verifique sua cota na Google AI Studio.")
            print("="*50 + "\n")
        # Auth Errors
        elif "invalid_api_key" in error_msg or "401" in error_msg or "403" in error_msg or "InvalidArgument" in error_msg:
            print("\n" + "="*50)
            print("ERRO DE AUTENTICAÇÃO:")
            print("Sua API Key parece inválida ou sem permissão.")
            print("Solução: Verifique o arquivo .env e sua chave.")
            print("="*50 + "\n")
        else:
            print(f"\nErro inesperado durante a ingestão: {e}")

if __name__ == "__main__":
    if not os.path.exists("document.pdf"):
        print("Error: document.pdf not found in current directory.")
    else:
        ingest("document.pdf")
