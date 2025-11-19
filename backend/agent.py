from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import noise_cancellation, google
from RAG import search_faiss  

load_dotenv(".env")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful store assistant. When answering store-related questions "
                "(hours, location, parking, services, payment, returns, accessibility, contact), "
                "you MUST call the `search_store_info` tool to retrieve accurate information. "
                "Base your answer ONLY on the returned information. "
                "If the tool returns no relevant data, say you don't have that specific info "
                "and recommend contacting the store directly. "
                "For non-store questions, answer using your general knowledge. "
                "Keep responses concise and friendly for voice interaction."
            )
        )

    @function_tool(name="search_store_info", description=( "Search the store knowledge base for information about hours, location, "
            "parking, services, payment methods, returns policy, accessibility, or contact details. "
            "Call this tool whenever the user asks about the store." ))
    async def search_store_info(self, query: str) -> str:
        # Retrieves relevant store information from FAISS vector database.
        # Returns relevant store information as formatted text, or empty string if nothing found
        
        if not query or not query.strip():
            return "No query provided."
        
        print(f"\n RAG Tool Called with query: {query}")
        
        try:
            # Perform FAISS search
            results = search_faiss(query, k=5)
            
            if not results:
                return "No relevant store information found for this query."
            
            # Filter and clean results
            valid_results = [r.strip() for r in results if r and r.strip()]
            
            if not valid_results:
                return "No relevant store information found for this query."
            
            context = "\n\n---\n\n".join(valid_results)
            
            print(f" Retrieved {len(valid_results)} relevant chunks")
            
            return f"[STORE INFORMATION]\n\n{context}\n\n[END OF STORE INFORMATION]"
            
        except Exception as e:
            print(f"RAG Error: {e}")
            import traceback
            traceback.print_exc()
            return f"Error searching store information: {str(e)}"


async def entrypoint(ctx: agents.JobContext):
    system_instructions = (
        "You are a friendly store assistant with access to a store knowledge base via tools. "
        "For ANY question about store hours, location, parking, services, payment methods, "
        "returns policy, accessibility features, or contact information: "
        "1. Call the `search_store_info` tool with the user's query "
        "2. Use ONLY the information returned by the tool "
        "3. Answer naturally and conversationally "
        "4. Don't mention 'the tool' or 'the database' - just answer directly "
        "\n"
        "If the tool returns no relevant information, politely say: "
        "\"I don't have specific information about that right now, but you can contact "
        "the store directly for more details.\" "
        "\n"
        "For questions unrelated to the store, use your general knowledge to help. "
        "Keep all responses friendly for voice interaction."
    )

    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",
            voice="Puck",
            temperature=0.3,  
            instructions=system_instructions,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(
        instructions=(
            "Greet the user warmly and introduce yourself as their store assistant. "
            "Briefly mention you can help with store hours, location, parking, services, "
            "and any other store questions. Keep it friendly"
        )
    )

    print("\n Voice agent with FAISS RAG tool is ready!")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))