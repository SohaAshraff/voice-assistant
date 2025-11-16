from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = os.getenv("LIVEKIT_URL")  

class TokenRequest(BaseModel):
    room_name: str = "voice-ai-room"
    participant_name: str = "user"

@app.post("/token")
def get_token(request: TokenRequest):
    try:
        if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
            raise HTTPException(status_code=500, detail="Missing LiveKit credentials")

        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)

        token.with_grants(
            api.VideoGrants(
                room=request.room_name,
                room_join=True,
                can_publish=True,
                can_subscribe=True,
            )
        )

        return {
            "token": token.to_jwt(),
            "url": LIVEKIT_URL,
            "room_name": request.room_name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    if not all([LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL]):
        print(" ERROR: Missing LiveKit credentials in .env file!")
        print("Required variables:")
        print("  - LIVEKIT_API_KEY")
        print("  - LIVEKIT_API_SECRET")
        print("  - LIVEKIT_URL")
        exit(1)
    
    print("=" * 50)
    print(" FastAPI Token Server Starting...")
    
    uvicorn.run(app, host="0.0.0.0", port=5000)