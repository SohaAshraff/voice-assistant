
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation, google
from RAG import search_faiss

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful AI assistant for a store with access to store information.

IMPORTANT RULES:
1. If the user asks about store-related topics (hours, location, services, contact, parking, payment, returns, etc.), use ONLY the provided store information.
2. Always check the provided context carefully before answering.
3. If the question is unrelated to the store, answer using your general knowledge.
4. If you don't have specific store information to answer, say: "I don't have specific information about this, but you can contact the store directly for more details."
5. Be conversational and friendly.
6. Keep responses concise for voice interaction.
"""
        )


async def entrypoint(ctx: agents.JobContext):
    system_instructions = """You are a friendly store assistant with access to a complete store knowledge base.

CRITICAL: When you receive context from the knowledge base, READ IT CAREFULLY and use it to answer.

The knowledge base includes information about:
- Store hours and location
- Parking availability (FREE parking is available!)
- Services offered
- Payment methods
- Return policy
- Contact information
- Accessibility features

When answering:
1. Check if the provided context answers the question
2. Use the exact information from the context
3. Be natural and conversational
4. Don't mention "the knowledge base" or "retrieved information"

If no relevant context is provided, say you don't have that specific information."""

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.6,
            instructions=system_instructions,
        ),
    )

    original_generate = session.generate_reply

    async def rag_enhanced_generate(*args, **kwargs):
        instructions = kwargs.get("instructions", "")

        # Apply RAG for substantial user queries
        if instructions and len(instructions) > 20:
            print(f"\n User Query: {instructions}")

            try:
                # Retrieve relevant context from FAISS 
                rag_results = search_faiss(instructions, k=5)
                
                if rag_results and len(rag_results) > 0:
                    # Filter out empty results
                    valid_results = [r.strip() for r in rag_results if len(r.strip()) > 0]
                    
                    if valid_results:
                        context_text = "\n\n---\n\n".join(valid_results)
                        
                        enhanced_instructions = f"""You are answering a question about our store. Here is the EXACT information from our database:

{context_text}

The customer asked: "{instructions}"

IMPORTANT: Use the information above to answer. For example:
- If they ask about parking: Tell them we have FREE parking in our lot behind the building (entrance on Oak Street) + validated parking across the street for up to 3 hours
- If they ask about hours: Give them the exact hours from the information above
- If they ask about location: Give them the exact address and directions

Answer naturally and concisely as if you're speaking to them. Don't say things like "according to our records" - just give them the information directly.
"""
                        kwargs["instructions"] = enhanced_instructions
                        
                        print(f" RAG: Retrieved {len(valid_results)} relevant chunks")
                        print(f" Context preview:")
                        for i, chunk in enumerate(valid_results[:2], 1):
                            preview = chunk[:150].replace('\n', ' ')
                            print(f"   {i}. {preview}...")
                    else:
                        print(" RAG: Retrieved chunks were empty")
                else:
                    print(" RAG: No results returned")
                    
            except Exception as e:
                print(f" RAG Error: {e}")
                import traceback
                traceback.print_exc()

        return await original_generate(*args, **kwargs)

    session.generate_reply = rag_enhanced_generate

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions="Hello! Greet the user warmly and introduce yourself as the store assistant. Mention you can help with questions about store hours, location, parking, services, or any store-related questions. Keep it brief and friendly."
    )

    print("\n✅ Voice agent with FAISS RAG is ready!")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))