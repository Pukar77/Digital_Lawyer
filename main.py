import os
from dotenv import load_dotenv

try:
    from src.pdf_loader import PDFLoader
    from src.text_splitter import ConstitutionSplitter
    from src.vector_store import QdrantHandler
except ImportError as e:
    print(f"❌ Error importing custom modules: {e}")
    print("Please ensure your src directory contains pdf_loader.py, text_splitter.py, and vector_store.py.")
    exit()


load_dotenv()  

def main():
    
    DOCUMENT_TITLE = os.getenv("DOCUMENT_TITLE", "The Constitution of Nepal") 
    COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "nepal_constitution_v1")
    PDF_PATH = "data/Nepal_Law.pdf" 
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ File not found: {PDF_PATH}")
        return

    # 1. Load & Clean
    print("Step 1: Loading and cleaning PDF...")
    loader = PDFLoader(PDF_PATH)
    clean_text = loader.load_and_clean()
    
    # 2. Split & Chunk
   
    print(f"Step 2: Splitting text by Article (Document Title: {DOCUMENT_TITLE})...")
    splitter = ConstitutionSplitter(document_title=DOCUMENT_TITLE)
    chunks = splitter.split_and_chunk(clean_text)
    
    
    if chunks:
        print(f"📝 Generated {len(chunks)} Article-level chunks.")
        print(f"First chunk metadata: {chunks[0]['metadata']}")
    
    # 3. Store in Vector DB (Qdrant Docker)
    print(f"Step 3: Storing data in Qdrant collection: {COLLECTION_NAME}...")
    qdrant = QdrantHandler(collection_name=COLLECTION_NAME)
 
    
    qdrant.store_data(chunks)
    
    print("\n---------------------------------------------------")
    print("✅ Ingestion complete. Qdrant is populated.")
    print("---------------------------------------------------")
    print("Next Steps: Run 'streamlit run app.py' to start your application.")


if __name__ == "__main__":
    main()