
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import numpy as np
import faiss

with open("store.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,  
    chunk_overlap=50,  
    separators=["\n\n", "\n", ". ", "! ", "? ", ", "]  
)

chunks = text_splitter.split_text(full_text)
print(f" Total Chunks: {len(chunks)}")
print("\n Sample chunks:")
for i, chunk in enumerate(chunks[:3]):
    print(f"\n--- Chunk {i+1} ---")
    print(chunk[:150] + "..." if len(chunk) > 150 else chunk)

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(np.array(embeddings))

print(f"\n FAISS index created with {index.ntotal} vectors")


def search_faiss(query, k=5):  
    #Search for relevant chunks in the store knowledge base
    print(f"\n Searching for: '{query}'")
    
    query_emb = model.encode([query])
    
    distances, indices = index.search(query_emb, k)
    
    results = []
    for i, (idx, dist) in enumerate(zip(indices[0], distances[0])):
        chunk = chunks[idx]
        print(f"  Result {i+1} (score: {dist:.2f}): {chunk[:100]}...")
        results.append(chunk)
    
    # Filter out duplicates
    unique_results = []
    seen = set()
    for r in results:
        if r not in seen:
            unique_results.append(r)
            seen.add(r)
    
    return unique_results[:k]


# # Test the search function
# if __name__ == "__main__":
#     test_queries = [
#         "What are the store hours?",
#         "Where is the store located?",
#         "Do you have wheelchair access?"
#     ]
    
#     for query in test_queries:
#         print(f"\n Query: {query}")
#         results = search_faiss(query, k=2)
#         print(f" Found {len(results)} relevant chunks\n")