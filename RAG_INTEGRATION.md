# 🧠 RAG (Retrieval-Augmented Generation) – Store Assistant

This document explains the RAG system used in this project, including:

* FAISS vector search
* SentenceTransformers embeddings
* LiveKit + Gemini Realtime
* **Function calling via `search_store_info`** ✔ (NEW SECTION INCLUDED)

---

# 📌 Table of Contents

1. [What is RAG?](#what-is-rag)
2. [How the System Works](#how-the-system-works)
3. [Knowledge Base](#knowledge-base)
4. [Chunking & Embeddings](#chunking--embeddings)
5. [FAISS Vector Search](#faiss-vector-search)
6. [Function Tool – `search_store_info`](#function-tool--search_store_info)
7. [Function Calling Workflow](#function-calling-workflow)
8. [Code Flow Diagram](#code-flow-diagram)
9. [Example Interaction](#example-interaction)
10. [Troubleshooting](#troubleshooting)

---

# ❓ What is RAG?

RAG improves AI responses by retrieving relevant text from a knowledge base before generating an answer.

### Without RAG

```
User: When do you close?
AI: I’m not sure.
```

### With RAG

```
User: When do you close?
AI → Searches data → Finds store hours
AI: We close at 10 PM on weekdays and 11 PM weekends.
```

---

# ⚙️ How the System Works

If the user asks any store-related question (hours, location, returns, parking, contact, etc.), the AI:

1. Calls the `search_store_info` function tool
2. The tool performs a FAISS vector similarity search
3. The tool returns relevant store information
4. The AI must respond **using only that information**

If no result exists:

> The AI politely tells the user it doesn’t have that info.

---

# 📚 Knowledge Base

Stored in:

```
store.txt
```

Plain text file containing information about:

* Store hours
* Location
* Parking
* Services
* Payment
* Returns
* Accessibility
* Contact details

To update the knowledge base, **edit this file only**.

---

# ✂️ Chunking & Embeddings

The file is split into overlapping chunks:

```python
chunk_size = 300
chunk_overlap = 50
```

This allows:

* Cleaner contextual retrieval
* Less information loss at boundaries

Embeddings use:

```python
SentenceTransformer("all-MiniLM-L6-v2")
```

Each chunk becomes a 384-dimensional semantic vector.

---

# ⚡ FAISS Vector Search

FAISS is used for fast nearest-neighbor similarity search:

```python
index = faiss.IndexFlatL2(d)
index.add(embeddings)
```

Searching:

```python
search_faiss(query, k=5)
```

Returns the top-K most relevant text chunks based on meaning, not keywords.

---

# 🧰 Function Tool – `search_store_info`

This system uses a **structured function tool**, defined as:

```python
@function_tool(
    name="search_store_info",
    description=(
        "Search the store knowledge base for information about hours, "
        "location, parking, services, payment methods, returns policy, "
        "accessibility, or contact details. "
        "Call this tool whenever the user asks about the store."
    )
)
```

### What this means

📌 When Gemini receives a question such as:

```
"What time do you close?"
```

It detects that this is a **store-related question**, and automatically calls:

```python
search_store_info("What time do you close?")
```

### What the function does

Inside the function:

1. Converts user question to an embedding
2. Searches FAISS vector index
3. Retrieves matching text chunks
4. Formats them as:

```
[STORE INFORMATION]
...
[END OF STORE INFORMATION]
```

5. Returns the result to the LLM

The LLM **must base its answer only on this returned text.**

---

# 🧠 How the Assistant Enforces Function Use

The agent instructions clearly state:

```
When answering store-related questions (
hours, location, parking, services, payment, 
returns, accessibility, contact),
you MUST call the `search_store_info` tool.
```

Also:

* If results exist → answer using them
* If no results → politely say you don’t have that info
* The AI should answer naturally, without mentioning “tools” or “FAISS”

So the LLM is guided to:

* Decide whether the question is store-related
* Trigger the correct function
* Use factual data only

---

# 🔁 Function Calling Workflow

Full pipeline:

```
User speaks
    ↓
LiveKit captures audio
    ↓
Gemini transcribes text
    ↓
LLM checks the task
    ↓
Is the question about the store?
    ↓       ↓
  Yes        No
    ↓        ↓
Call search_store_info()     Answer directly
    ↓
FAISS returns relevant chunks
    ↓
LLM reads chunks
    ↓
Generates a natural human answer
    ↓
Gemini converts text to speech
    ↓
User hears the final answer
```

---

# 💬 Example Interaction

### User

> Where is the store located?

### Console Output

```
RAG Tool Called with query: Where is the store located?

Searching for: 'Where is the store located?'
Result 1 (score 0.42): Address: Downtown Street 12, Cairo, Egypt...
Result 2 (score 1.11): Contact information...
```

### Assistant Response

> The store is located at Downtown Street 12 in Cairo, next to City Center Mall.

---

# 🧪 Testing the RAG System

Run:

```bash
python RAG.py
```

You should see:

* Number of chunks created
* Example chunk outputs
* Search results with similarity scores

---

# 🛠 Troubleshooting

### ❗ Low-quality retrieval

* High distances (>1.5)
* Wrong chunks returned

Try:

* Increase chunk size:

```python
chunk_size = 400
```

* Increase number of retrieved chunks:

```python
search_faiss(query, k=7)
```

---

### ❗ Model retrieves results but AI ignores them

Strengthen function tool instructions to:

```
Base your answer ONLY on the information returned by `search_store_info`.
```

---

### ❗ Search slow

Check runtime:

```python
import time
start = time.time()
search_faiss("test")
print(time.time() - start)
```

Typical time: **< 10 ms**

---

# 🧾 Summary

| Component       | Technology                        |
| --------------- | --------------------------------- |
| Vector DB       | FAISS                             |
| Embeddings      | SentenceTransformer               |
| Store data      | store.txt                         |
| Retrieval       | search_store_info() function tool |
| LLM enforcement | System instructions               |

This setup ensures:

* Accurate, real store answers
* No hallucination
* Easy updates
* Local and fast retrieval

---

