# 🧠 RAG Integration Documentation

## Retrieval-Augmented Generation with Gemini Live API

This document details how the RAG (Retrieval-Augmented Generation) system integrates with Google's Gemini Live API to provide accurate, context-aware responses.

---

## Table of Contents

1. [What is RAG?](#what-is-rag)
2. [System Components](#system-components)
3. [How Retrieval Works](#how-retrieval-works)
4. [Integration with Gemini](#integration-with-gemini)
5. [Example Walkthrough](#example-walkthrough)
6. [Performance Analysis](#performance-analysis)
7. [Troubleshooting](#troubleshooting)

---

## What is RAG?

**Retrieval-Augmented Generation** is a technique that enhances AI responses by retrieving relevant information from a knowledge base before generating an answer.

### Why RAG?

**Without RAG:**
```
User: "What's the store location?"
AI: "I don't have specific information about location."
```

**With RAG:**
```
User: "What's the store location?"
System: [Searches knowledge base → Finds location info]
AI: "Our store is located at 123 Main Street, Downtown, NY..."
```

### Benefits

✅ **Accuracy:** Uses verified store data  
✅ **Up-to-date:** Easy to update knowledge base  
✅ **Traceable:** Can verify sources  
✅ **Specific:** Provides exact details (hours, addresses, etc.)  

---

## System Components

### 1. Knowledge Base (`store.txt`)

**Format:** Plain text with sections

**Structure:**
- Each section starts with a topic keyword
- Clear, concise information
- Natural language format

---

### 2. Text Splitter (RAG.py)

**Purpose:** Break knowledge base into searchable chunks


| Parameter | Value | Reason |
|-----------|-------|--------|
| `chunk_size` | 300 | Long enough for complete context |
| `chunk_overlap` | 50 | Prevents information loss at boundaries |
| `separators` | Natural breaks | Keeps related info together |

---

### 3. Embedding Model (RAG.py)

**Model:** `all-MiniLM-L6-v2` by Sentence Transformers

**Specifications:**
- Input: Text string (any length)
- Output: 384-dimensional vector
- Language: English (optimized)

**What Are These Vectors?**

Embeddings capture semantic meaning:

Similar meanings = Similar vectors

---

### 4. Vector Database - FAISS (RAG.py)

**FAISS:** Facebook AI Similarity Search

**Purpose:** Fast nearest neighbor search in high-dimensional space


## How Retrieval Works

### Complete Flow from User Question to Response

```
┌─────────────────────────────────────────────────────────────┐
│                     User Speaks                             │
│              "Where is the store location?"                 │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              LiveKit Audio Stream                            │
│         Audio transmitted to Voice Agent                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Gemini Live API                                │
│         Transcribes: "Where is the store location?"         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Agent Session (agent.py)                       │
│         Intercepts with rag_enhanced_generate()             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              RAG System (RAG.py)                            │
│                                                             │
│  1. Encode query to vector:                                 │
│                                                             │
│  2. Search FAISS index:                                     │
│     Find 5 nearest chunks                                   │
│                                                             │
│  3. Results with scores                                     │                          
│                                                             │
│  4. Return top 5 chunks                                     │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Enhanced Prompt Builder (agent.py)             │
│                                                             │
│  Creates enriched prompt:                                   │
│                                                             │
│  "You are answering about our store. Here is EXACT info:    │
│                            .........                        │                
│                                                             │
│   Use the information above to answer..."                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Gemini Response Generation                     │
│                                                             │
│  Reads context, generates natural response                  │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Text-to-Speech (Gemini)                        │
│         Converts response to audio (Puck voice)             │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              LiveKit Audio Stream                           │
│         Audio transmitted back to user                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              User Hears Response                            │
│         Response played in browser                          │
└─────────────────────────────────────────────────────────────┘
```

### Why This Approach?

**Advantages:**
- ✅ Works with every user message
- ✅ Automatic context injection
- ✅ Simpler implementation

---

## Example Walkthrough

### Example 1: Store Hours

**User:** "What time do you close?"

**Terminal Output:**
```
 User Query: What time do you close?

 Searching for: 'What time do you close?'
  Result 1 (score: 0.61): opening hours : Our store is open Monday to Friday from 9:00 AM to 6:00 PM. On Saturdays, we're open...
  Result 2 (score: 1.28): location: We are located at 123 Main Street, Downtown, NY 10001. The store is right next to the City...
  Result 3 (score: 1.35): parking: free parking is available in our lot behind the building. The parking lot entrance is on Oa...

✅ RAG: Retrieved 5 relevant chunks
```

**Score Analysis:**
- 0.61: **Perfect match** - Opening hours chunk
- 1.28: Good - Location (nearby context)
- 1.35: Acceptable - Parking (related)

**Agent Response:**
> "We close at 6:00 PM Monday through Friday, and at 5:00 PM on Saturdays. We're closed on Sundays and major holidays."

---

### Example 2: Location Question

**User:** "Where is the store located?"

**Terminal Output:**
```
🔍 User Query: Where is the store located?

🔎 Searching for: 'Where is the store located?'
  Result 1 (score: 0.81): location: We are located at 123 Main Street, Downtown, NY 10001. The store is right next to the City...
  Result 2 (score: 1.18): CONTACT INFORMATION: Phone: (555) 123-4567 Email: info@ourstore.com...
  Result 3 (score: 1.35): opening hours : Our store is open Monday to Friday...

✅ RAG: Retrieved 5 relevant chunks
```

**Agent Response:**
> "We're located at 123 Main Street, Downtown, NY 10001. We're right next to the City Hall subway station on the blue line. There's a coffee shop on the corner - we're in the same building."

---



## Code Flow Diagram

```python
# User speaks in browser
    ↓
# LiveKit transmits audio
    ↓
# Gemini transcribes speech
    ↓
# agent.py receives transcription

async def rag_enhanced_generate(*args, **kwargs):
    instructions = kwargs.get("instructions", "")  # ← User query
    
    if instructions and len(instructions) > 20:
        # STEP 1: Call RAG
        rag_results = search_faiss(instructions, k=5)
        
        # STEP 2: Filter results
        valid_results = [r.strip() for r in rag_results 
                        if len(r.strip()) > 0]
        
        if valid_results:
            # STEP 3: Build context
            context_text = "\n\n---\n\n".join(valid_results)
            
            # STEP 4: Create enhanced prompt
            enhanced_instructions = f"""
            Here is store info: {context_text}
            Customer asked: {instructions}
            Use the info above to answer.
            """
            
            # STEP 5: Replace instructions
            kwargs["instructions"] = enhanced_instructions
    
    # STEP 6: Call Gemini with enhanced prompt
    return await original_generate(*args, **kwargs)

# Gemini generates response with context
    ↓
# Text-to-speech conversion
    ↓
# LiveKit transmits audio back
    ↓
# User hears response
```

---

## Troubleshooting

### Issue 1: Poor Retrieval Results

**Symptoms:**
- All scores above 1.5
- Agent says "I don't know" despite having info

**Solutions:**

```python
# 1. Test RAG directly
python RAG.py

# 2. Check chunks were created

# 3. Increase k value
search_faiss(query, k=5)  # Try k=7 or k=10

# 4. Adjust chunk size in RAG.py
chunk_size=400  # From 300
```

---

### Issue 2: Agent Ignores Context

**Symptoms:**
- Context retrieved (scores good)
- Agent still doesn't use information

**Solution:**

Strengthen the prompt in `agent.py`:

```python
enhanced_instructions = f"""CRITICAL: You MUST use this information:

{context_text}

Customer question: {instructions}

Answer ONLY using the information above. Read it carefully."""
```

---

### Issue 3: Slow Performance

**Check:**
```python
import time

start = time.time()
results = search_faiss("test query")
print(f"Search took: {(time.time()-start)*1000:.2f}ms")
```

**If slower:**
- Model loading on every call (load once!)
- Large chunk size (reduce to 250)
- Too many chunks (>1000 needs IndexIVFFlat)

---
