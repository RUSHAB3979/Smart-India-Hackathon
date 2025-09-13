import gradio as gr
import pandas as pd
from transformers import pipeline
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io


print("Loading models...")
sentiment_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
print("Models loaded successfully!")


def analyze_sentiment(comment):
    candidate_labels = ["Supportive", "Opposed", "Suggesting an amendment", "Asking a question"]
    prediction = sentiment_classifier(comment, candidate_labels)
    confidences = {label: score for label, score in zip(prediction['labels'], prediction['scores'])}
    return confidences

def summarize_text(comment):
    if len(comment.split()) > 30:
        summary = summarizer(comment, max_length=100, min_length=25, do_sample=False)
        return summary[0]['summary_text']
    else:
        return "The comment is too short to summarize. Summaries work best for comments longer than 30 words."

def generate_word_cloud(file_obj):
    df = pd.read_csv(file_obj.name)
    if 'comment_text' in df.columns:
        text_corpus = " ".join(comment for comment in df.comment_text if isinstance(comment, str))
    else:
        text_corpus = " ".join(comment for comment in df.iloc[:, 0] if isinstance(comment, str))
    
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_corpus)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.tight_layout(pad=0)
    
    return plt


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# MCA eConsultation AI Analyzer")
    with gr.Tabs():
        with gr.TabItem("Single Comment Analysis"):
            with gr.Row():
                sentiment_input = gr.Textbox(lines=10, label="Paste Stakeholder Comment Here")
                sentiment_output = gr.Label(num_top_classes=4, label="Sentiment Analysis")
            sentiment_button = gr.Button("Analyze Sentiment")

        with gr.TabItem("Summary Generation"):
            with gr.Row():
                summary_input = gr.Textbox(lines=10, label="Paste Long Comment Here")
                summary_output = gr.Textbox(label="Generated Summary", interactive=False)
            summary_button = gr.Button("Generate Summary")

        with gr.TabItem("Overall Word Cloud"):
            gr.Markdown("Upload a CSV file containing all comments to generate a word cloud. The file should have a column named `comment_text`.")
            wordcloud_input = gr.File(label="Upload Comments CSV")
            wordcloud_output = gr.Plot(label="Keyword Density Word Cloud") # CORRECTED LINE
            wordcloud_button = gr.Button("Generate Word Cloud")

    sentiment_button.click(analyze_sentiment, inputs=sentiment_input, outputs=sentiment_output)
    summary_button.click(summarize_text, inputs=summary_input, outputs=summary_output)
    wordcloud_button.click(generate_word_cloud, inputs=wordcloud_input, outputs=wordcloud_output)

if __name__ == "__main__":
    demo.launch(share=True)