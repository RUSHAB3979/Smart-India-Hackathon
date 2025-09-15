from flask import Flask, request, redirect, url_for, Response, session, render_template

app = Flask(__name__)
app.secret_key = "shubham_secret"

ADMIN_CREDENTIALS = {"admin": "admin123"}

USER_CREDENTIALS = {"Shubham": "0604"}

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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if USER_CREDENTIALS.get(username) == password:
            session["user"] = username
            return redirect(url_for("home"))
        if ADMIN_CREDENTIALS.get(username) == password:
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return Response("Invalid User Credentials!")
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
        link = request.form.get("link", "")
        acts_list.append({"title": title, "type": type_, "date": date, "link": link})

    return render_template("admin_dashboard.html", gr_list=acts_list)

@app.route("/admin-logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/acts")
def acts():
    return render_template("acts.html", acts=acts_list)

@app.route("/econsultation")
def econsultation():
    return render_template("econsultation.html")

if __name__ == "__main__":
    app.run(debug=True)
