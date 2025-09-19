from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

CSV_FILE = "feedback.csv"

# Ensure CSV file has headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["comment_id", "comment_text"])  # headers


def read_feedbacks():
    feedbacks = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            feedbacks.append(row)
    return feedbacks


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        comment = request.form.get("comment")

        # Auto-increment comment_id
        feedbacks = read_feedbacks()
        comment_id = len(feedbacks) + 1

        # Save feedback
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([comment_id, comment])

        return redirect(url_for("home"))

    # Read feedbacks
    feedbacks = read_feedbacks()

    # Stats
    total_comments = len(feedbacks)
    unique_stakeholders = total_comments  # since we no longer track names

    return render_template(
        "index.html",
        feedbacks=feedbacks,
        total_comments=total_comments,
        unique_stakeholders=unique_stakeholders,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
