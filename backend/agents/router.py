import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

# 🔥 YAHAN APNI GEMINI API KEY PASTE KARO
api_key = os.getenv("GEMINI_API_KEY")

# LangChain ke liye environment variable set kar rahe hain
os.environ["GOOGLE_API_KEY"] = api_key

def detect_intent_and_route(user_query):
    try:
        # Latest standard model use kar rahe hain
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        
        prompt = f"""
        You are an AI Router for TechMart Electronics customer support. 
        Analyze the user query and classify it into EXACTLY ONE or TWO of these specific categories based on our company departments:
        
        1. BILLING - For payment issues, subscription locks, invoices, or refund requests.
        2. TECHNICAL - For installation errors, password resets, system crashes, or hardware bugs.
        3. PRODUCT - For laptop/mobile specifications, pricing, features, and comparisons.
        4. COMPLAINT - For customer dissatisfaction, damaged shipments, or escalations.
        5. FAQ - For general questions about delivery time, tracking orders, or shipping policies.
        
        Return ONLY the category names comma-separated. Do not write full sentences or any other text.
        
        Examples:
        Query: "I paid for premium but it is still locked." -> Output: BILLING, TECHNICAL
        Query: "What is the price and RAM of the Pro laptop?" -> Output: PRODUCT
        Query: "My package arrived broken." -> Output: COMPLAINT, FAQ
        
        Query: "{user_query}"
        Output:"""
        
        response = llm.invoke(prompt)
        intents = [intent.strip().upper() for intent in response.content.split(",")]
        return intents
    except Exception as e:
        return [f"ERROR: {str(e)}"]

if __name__ == "__main__":
    print("--- Testing Router with LangChain & Gemini ---")
    
    test_1 = "I paid yesterday but my Premium feature is still locked."
    print(f"Query: {test_1} -> Routed To: {detect_intent_and_route(test_1)}")
    
    test_2 = "How much RAM does the TechMart Pro laptop have?"
    print(f"Query: {test_2} -> Routed To: {detect_intent_and_route(test_2)}")