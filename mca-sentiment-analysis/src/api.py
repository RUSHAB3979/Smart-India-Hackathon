from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import requests
import json

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Ollama API URL
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def classify_comment_with_ollama(comment: str):
    
    prompt = f"""
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert assistant analyzing stakeholder feedback. Classify the user's comment into one of four categories: Supportive, Opposed, Suggesting an amendment, or Asking a question. Provide only the single-word classification.
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Comment: "{comment}"
    Classification:<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """
    payload = {"model": "llama3", "prompt": prompt, "stream": False}
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        data = json.loads(response.text)
        return data.get('response', 'Unknown').strip()
    except Exception:
        return "Error"

# --- Define the API Endpoint ---
@app.get("/dashboard-data")
async def get_dashboard_data():
    """
    This is the function your team's website will call.
    It reads comments, analyzes them, and returns a summary.
    """
    try:
        # For the demo, we'll read from a simple CSV file.
        # Your team's website could also be writing to this file.
        df = pd.read_csv("data/live_comments.csv")
        
        # Ensure the column exists and is not empty
        if 'comment_text' not in df.columns or df['comment_text'].isnull().all():
            return {"error": "No comments found"}

        comments = df['comment_text'].dropna().astype(str).tolist()
        
        # Analyze each comment
        classifications = [classify_comment_with_ollama(c) for c in comments]
        
        # Calculate the sentiment breakdown
        sentiment_counts = pd.Series(classifications).value_counts().to_dict()
        
        return {
            "total_comments": len(comments),
            "sentiment_breakdown": sentiment_counts,
            "latest_comments": comments[-5:] # Return the 5 most recent comments
        }
    except FileNotFoundError:
        return {"error": "data/live_comments.csv not found."}
    except Exception as e:
        return {"error": str(e)}
