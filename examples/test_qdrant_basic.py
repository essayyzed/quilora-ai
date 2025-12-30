"""
Quick test of Qdrant Document Store

Prerequisites:
1. Start Qdrant locally:
   docker run -p 6333:6333 qdrant/qdrant

2. Run this script:
   uv run python examples/test_qdrant_basic.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from haystack import Document
from src.document_stores.store import QdrantDocumentStore

def main():
    print("🔧 Initializing Qdrant Document Store...")
    store = QdrantDocumentStore(
        collection_name="test_collection",
        embedding_dimension=128,
    )
    
    print(f"📊 Current document count: {store.count_documents()}")
    
    # Create sample documents with embeddings
    print("\n📝 Creating sample documents...")
    docs = [
        Document(
            id="doc1",
            content="The quick brown fox jumps over the lazy dog.",
            embedding=[0.1] * 128,  # Fake embedding for demo
            meta={"source": "example", "category": "animals"},
        ),
        Document(
            id="doc2",
            content="Machine learning is a subset of artificial intelligence.",
            embedding=[0.5] * 128,
            meta={"source": "example", "category": "tech"},
        ),
        Document(
            id="doc3",
            content="Python is a popular programming language for data science.",
            embedding=[0.7] * 128,
            meta={"source": "example", "category": "tech"},
        ),
    ]
    
    # Write documents
    print("💾 Writing documents to Qdrant...")
    written = store.write_documents(docs)
    print(f"✅ Wrote {written} documents")
    
    # Count
    count = store.count_documents()
    print(f"📊 Total documents: {count}")
    
    # Search
    print("\n🔍 Searching for similar documents...")
    query_embedding = [0.6] * 128  # Similar to tech docs
    results = store.search(query_embedding, top_k=2)
    
    print(f"Found {len(results)} results:")
    for i, doc in enumerate(results, 1):
        print(f"  {i}. [{doc.score:.3f}] {doc.content[:50]}...")
        print(f"     Category: {doc.meta.get('category')}")
    
    # Search with filter
    print("\n🔍 Searching with filter (category=tech)...")
    filtered_results = store.search(
        query_embedding,
        top_k=5,
        filters={"category": "tech"},
    )
    print(f"Found {len(filtered_results)} tech documents")
    
    # Delete one document
    print("\n🗑️  Deleting document 'doc1'...")
    deleted = store.delete_documents(document_ids=["doc1"])
    print(f"✅ Deleted {deleted} document(s)")
    print(f"📊 Remaining documents: {store.count_documents()}")
    
    # Cleanup
    print("\n🧹 Cleaning up test collection...")
    store.delete_collection()
    print("✅ Done!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure Qdrant is running:")
        print("  docker run -p 6333:6333 qdrant/qdrant")
