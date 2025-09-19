from flask import Flask, request, redirect, url_for, Response, session, render_template
import csv, os

app = Flask(__name__)
app.secret_key = "shubham_secret"

# Dummy credentials
ADMIN_CREDENTIALS = {"admin": "admin123"}
USER_CREDENTIALS = {"Shubham": "0604"}

# Acts data
acts_list = [
    {
        "title": "Companies Act, 2013",
        "type": "Act",
        "date": "29-08-2013",
        "image": "companies-act.jpg",
        "description": "Governs incorporation, regulation and dissolution of companies in India.",
        "pdf": "companies-act-2013.pdf"
    },
    {
        "title": "LLP Act, 2008",
        "type": "Act",
        "date": "31-03-2009",
        "image": "llp-act.jpg",
        "description": "Governs Limited Liability Partnerships in India.",
        "pdf": "llp-act-2008.pdf"
    }
]

# CSV file for feedback storage
CSV_FILE = "feedback.csv"

# Ensure CSV has headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["comment_id", "act_id", "name", "comment_text"])


# Helper function to read feedbacks
def read_feedbacks(act_id=None):
    feedbacks = []
    with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if act_id is None or str(row["act_id"]) == str(act_id):
                feedbacks.append(row)
    return feedbacks


# ---------------- AUTH ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if USER_CREDENTIALS.get(username) == password:
            session["user"] = username
            return redirect(url_for("home"))
        if ADMIN_CREDENTIALS.get(username) == password:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            return Response("Invalid Credentials!")
    return render_template("login.html")


@app.route("/home")
def home():
    if "user" in session:
        return render_template("home.html", user=session["user"])
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ---------------- ADMIN ROUTES ----------------
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if ADMIN_CREDENTIALS.get(username) == password:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            return Response("Invalid Admin Credentials!")
    return render_template("admin_login.html")


@app.route("/admin-dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        title = request.form.get("title")
        type_ = request.form.get("type")
        date = request.form.get("date")
        description = request.form.get("description", "")
        pdf = request.form.get("pdf", "")
        image = request.form.get("image", "default.jpg")

        acts_list.append({
            "title": title,
            "type": type_,
            "date": date,
            "description": description,
            "pdf": pdf,
            "image": image
        })

    return render_template("admin_dashboard.html", gr_list=acts_list)


@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


# ---------------- USER ROUTES ----------------
@app.route("/acts")
def acts():
    return render_template("acts.html", acts=acts_list)


@app.route("/econsultation", methods=["GET", "POST"])
def econsultation():
    act_id = request.args.get("act", None)
    if act_id is None:
        return "No Act selected!", 400

    act = acts_list[int(act_id)] if act_id.isdigit() and int(act_id) < len(acts_list) else None
    if not act:
        return "Act not found!", 404

    if request.method == "POST":
        name = request.form.get("name")
        comment = request.form.get("comment")

        all_feedbacks = read_feedbacks()
        comment_id = len(all_feedbacks) + 1

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([comment_id, act_id, name, comment])

        return redirect(url_for("econsultation", act=act_id))

    feedbacks = read_feedbacks(act_id)
    total_comments = len(feedbacks)
    unique_stakeholders = len(set(f["name"] for f in feedbacks))

    return render_template(
        "econsultation.html",
        act=act,
        feedbacks=feedbacks,
        total_comments=total_comments,
        unique_stakeholders=unique_stakeholders,
    )


if __name__ == "__main__":
    app.run(debug=True)
