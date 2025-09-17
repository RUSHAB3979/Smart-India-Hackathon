from flask import Flask, render_template
from wordcloud import WordCloud
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

@app.route("/")
def home():
    df = pd.read_csv("static/comments.csv")
    text = " ".join(df["comment_text"].astype(str))


    # Generate wordcloud
    wordcloud = WordCloud(
        width=1000,
        height=600,
        background_color="white",
        colormap="tab10",
        collocations=False
    ).generate(text)

    # Make sure the static folder exists
    if not os.path.exists("static"):
        os.makedirs("static")

    wordcloud.to_file("static/wordcloud.png")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
