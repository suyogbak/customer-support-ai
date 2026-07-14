import os
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS
# Yahan hum badal kar HuggingFace Embeddings le aaye hain
from langchain_community.embeddings import HuggingFaceEmbeddings

# Local vector database save karne ka raasta
DB_FAISS_PATH = "vectorstore/db_faiss"

def build_vector_db():
    pdf_dir = "../knowledge_base"
    documents_chunks = []
    
    if not os.path.exists(pdf_dir):
        print(f"❌ '{pdf_dir}' folder nahi mila! Pehle check karo.")
        return

    for file in os.listdir(pdf_dir):
        if file.endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, file)
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            # Text ko 500-500 characters ke chunks me todna
            chunks = [text[i:i+500] for i in range(0, len(text), 400)]
            documents_chunks.extend(chunks)
            print(f"📄 Processed {file}: Total {len(chunks)} chunks created.")

    if not documents_chunks:
        print("❌ Koyi chunks nahi bane. PDFs check karo!")
        return

    # 🔥 100% LOCAL MODEL: Google API ka jhanjhat hi khatam!
    print("⏳ Local Embedding Model load ho raha hai (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    print("⏳ Vector Database ban raha hai, thoda sabr rakhein...")
    db = FAISS.from_texts(documents_chunks, embeddings)
    db.save_local(DB_FAISS_PATH)
    print(f"✅ Vector Database successfully save ho gaya yahan: {DB_FAISS_PATH}")

def search_knowledge_base(query):
    # Search ke liye bhi local model use karenge
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    if not os.path.exists(DB_FAISS_PATH):
        return "No context available."
    
    # Local loading with safe deserialization
    db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(query, k=2) 
    
    context = "\n".join([doc.page_content for doc in docs])
    return context

if __name__ == "__main__":
    print("--- Building Knowledge Base Vector DB (Local Version) ---")
    build_vector_db()
    
    print("\n🔍 Testing Search:")
    test_search = search_knowledge_base("How much does the Pro laptop cost?")
    print("Matched Context Found:\n", test_search)