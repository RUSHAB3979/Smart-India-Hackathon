import gradio as gr
import pandas as pd
from wordcloud import WordCloud
import requests
import json

# Ollama API URL (runs locally)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

print("Application is ready. Using local Ollama with Llama 3.")


def analyze_sentiment(comment):
    
    prompt = f"""
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    You are an expert assistant analyzing stakeholder feedback for India's Ministry of Corporate Affairs. Your task is to classify user comments into one of four categories: Supportive, Opposed, Suggesting an amendment, or Asking a question. Pay close attention to sarcastic or nuanced comments where the literal meaning is inverted. Provide only the single-word classification as your final answer.
    
    -- High-Quality Examples --

    Comment: "I fully support the proposed changes to Section 135. This will enhance corporate social responsibility."
    Classification: Supportive

    Comment: "The proposal to increase the compliance burden for LLPs is deeply concerning and should be reconsidered."
    Classification: Opposed

    Comment: "I suggest that the timeline for private placement offers should be extended from 60 days to 90 days."
    Classification: Suggesting an amendment
    
    Comment: "Could the Ministry please clarify if this applies to foreign subsidiaries?"
    Classification: Asking a question

    Comment: "Wow, another brilliant policy that will have no real impact."
    Classification: Opposed

    Comment: "what a nuisance, wow"
    Classification: Opposed

    Comment: "This could be a good idea, but only if the scope is narrowed. As is, it's too broad."
    Classification: Suggesting an amendment
    <|eot_id|><|start_header_id|>user<|end_header_id|>
    Classify this new comment:
    Comment: "{comment}"
    Classification:<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    """

    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        response_text = response.text
        data = json.loads(response_text)
        classification = data.get('response', '').strip()

        labels = ["Supportive", "Opposed", "Suggesting an amendment", "Asking a question"]
        confidences = {label: 0.0 for label in labels}
        
        found = False
        for label in labels:
            if label.lower() in classification.lower():
                confidences[label] = 1.0
                found = True
                break
        
        if not found:
             return {"Error: Could not determine classification": 1.0, "Raw Response": classification}

        return confidences
    except Exception as e:
        return {str(e): 1.0}

def generate_word_cloud(file_obj):
    df = pd.read_csv(file_obj.name)
    if 'comment_text' in df.columns:
        text_corpus = " ".join(str(c) for c in df.comment_text.dropna())
    else:
        text_corpus = " ".join(str(c) for c in df.iloc[:, 0].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_corpus)
    return wordcloud.to_image()

# --- Create the Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# MCA eConsultation AI Analyzer (Powered by Llama 3)")
    with gr.Tabs():
        with gr.TabItem("Single Comment Analysis"):
            with gr.Row():
                sentiment_input = gr.Textbox(lines=10, label="Paste Stakeholder Comment Here")
                sentiment_output = gr.Label(num_top_classes=4, label="Sentiment Analysis")
            sentiment_button = gr.Button("Analyze Sentiment")

        with gr.TabItem("Overall Word Cloud"):
            gr.Markdown("Upload a CSV file with all comments to generate a word cloud.")
            wordcloud_input = gr.File(label="Upload Comments CSV")
            wordcloud_output = gr.Image(label="Keyword Density Word Cloud")
            wordcloud_button = gr.Button("Generate Word Cloud")

    sentiment_button.click(analyze_sentiment, inputs=sentiment_input, outputs=sentiment_output)
    wordcloud_button.click(generate_word_cloud, inputs=wordcloud_input, outputs=wordcloud_output)

# --- Launch The App ---
if __name__ == "__main__":
    demo.launch(share=True)
