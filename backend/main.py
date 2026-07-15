from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random
import bcrypt
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.router import detect_intent_and_route
from rag_processor import search_knowledge_base
from dotenv import load_dotenv

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

# 🔥 1. GEMINI API KEY SETUP
api_key = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = api_key


# 🗄️ 2. MONGO DB CLOUD CONNECTION (Yahan apni cloud link paste karo)
# Apne real password se <password> ko replace kar dena
MONGO_DETAILS = os.getenv("MONGO_DETAILS")
client = AsyncIOMotorClient(MONGO_DETAILS)
db = client.techmart_support_db
users_collection = db.get_collection("users")
chat_collection = db.get_collection("conversations")

# 🔒 3. PASSWORD HASHING SETUP


class UserAuth(BaseModel):
    username: str
    password: str

class ChatMessageSchema(BaseModel):
    username: str
    message: str

def analyze_sentiment(user_msg):
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        prompt = f"Analyze the sentiment of this customer message. Reply with ONLY one word: POSITIVE, NEUTRAL, or ANGRY.\nMessage: '{user_msg}'\nSentiment:"
        response = llm.invoke(prompt)
        return response.content.strip().upper()
    except:
        return "NEUTRAL"

# 🚀 REGISTER ENDPOINT
# 🔒 3. CRASH-FREE PASSWORD HASHING (Python 3.14+ Compatible)
# Purani pwd_context wali line ko hata kar ab hum direct bcrypt use karenge.

# 🚀 UPGRADED REGISTER ENDPOINT
@app.post("/api/auth/register")
async def register(user: UserAuth):
    existing_user = await users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists!")
    
    # Direct bcrypt hashing (No passlib bug)
    password_bytes = user.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    await users_collection.insert_one({"username": user.username, "password": hashed_password})
    return {"message": "Registration successful! Please login."}

# 🔑 UPGRADED LOGIN ENDPOINT
@app.post("/api/auth/login")
async def login(user: UserAuth):
    db_user = await users_collection.find_one({"username": user.username})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
        
    # Direct bcrypt verification
    password_bytes = user.password.encode('utf-8')
    db_password_bytes = db_user["password"].encode('utf-8')
    
    if not bcrypt.checkpw(password_bytes, db_password_bytes):
        raise HTTPException(status_code=400, detail="Invalid username or password")
        
    return {"status": "success", "username": user.username}


# 📜 HISTORY FETCH ENDPOINT
@app.get("/api/chat/history/{username}")
async def get_chat_history(username: str):
    cursor = chat_collection.find({"username": username}).sort("_id", 1)
    history = []
    async for doc in cursor:
        history.append({
            "sender": doc["sender"],
            "text": doc["text"],
            "intents": doc.get("intents"),
            "sentiment": doc.get("sentiment")
        })
    return history

# 💬 MAIN CHAT ENGINE WITH MEMORY & PERSISTENCE
@app.post("/api/chat")
async def chat_endpoint(request: ChatMessageSchema):
    user_msg = request.message
    username = request.username
    
    # Save User message to Cloud DB
    await chat_collection.insert_one({"username": username, "sender": "user", "text": user_msg})
    
    # CONVERSATION MEMORY (Fetch last 5 messages from Cloud DB)
    memory_cursor = chat_collection.find({"username": username}).sort("_id", -1).limit(5)
    past_chats = []
    async for doc in memory_cursor:
        past_chats.append(f"{doc['sender']}: {doc['text']}")
    past_chats.reverse()
    chat_memory_string = "\n".join(past_chats)

    sentiment = analyze_sentiment(user_msg)
    intents = detect_intent_and_route(user_msg)
    
    if sentiment == "ANGRY" or "COMPLAINT" in intents:
        ticket_id = f"TM-{random.randint(100000, 999999)}"
        escalation_msg = f"⚠️ [SENTIMENT: ANGRY DETECTED]\n\nWe apologize. Your issue is escalated to our Senior Manager.\n\n🎫 Ticket ID: {ticket_id}"
        await chat_collection.insert_one({"username": username, "sender": "bot", "text": escalation_msg, "intents": ["COMPLAINT", "ESCALATION"], "sentiment": sentiment})
        return {"intents": ["COMPLAINT", "ESCALATION"], "sentiment": sentiment, "ticket_id": ticket_id, "response": escalation_msg}

    retrieved_context = search_knowledge_base(user_msg)
    
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)
        system_prompt = f"""
        You are an expert Customer Support Agent for TechMart Electronics.
        Current Active Department Agents: {intents}.
        
        Company Knowledge Context:
        {retrieved_context}
        
        Recent Conversation History (Memory):
        {chat_memory_string}
        
        Answer the customer query professionally using the context and history.
        Response:"""
        
        response = llm.invoke(system_prompt)
        final_reply = response.content
    except Exception as e:
        final_reply = f"Facing internal routing issues. Please wait..."

    # Save Bot response to Cloud DB
    await chat_collection.insert_one({"username": username, "sender": "bot", "text": final_reply, "intents": intents, "sentiment": sentiment})

    return {"intents": intents, "sentiment": sentiment, "ticket_id": None, "response": final_reply}