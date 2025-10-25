from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .model.chatbot_engine import ChatbotEngine
from .database import SessionLocal, Conversation
from sqlalchemy.orm import Session
import logging
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = FastAPI(title="AI Chatbot Assistant", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chatbot engine
chatbot = ChatbotEngine()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = os.getenv("sk-abcd1234abcd1234abcd1234abcd1234abcd1234")
class ChatRequest(BaseModel):
    user_message: str

class TrainRequest(BaseModel):
    pass  # For future training data

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.user_message}")
        # Use OpenAI for response
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": request.user_message}
            ]
        )
        response = openai_response.choices[0].message.content

        # Save to database
        db: Session = SessionLocal()
        conversation = Conversation(user_input=request.user_message, bot_response=response)
        db.add(conversation)
        db.commit()
        db.close()

        return {"bot_response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/train")
async def train_endpoint(request: TrainRequest):
    try:
        logger.info("Starting model training")
        # Implement training logic here
        return {"message": "Training completed"}
    except Exception as e:
        logger.error(f"Error in train endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Training failed")

@app.get("/health")
async def health_endpoint():
    return {"status": "healthy"}
