from flask import Flask, render_template, request, url_for

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html")

@app.route("/register/sponsor", methods=["GET", "POST"])
def registerSponsor():
    if request.method == "POST":
        pass

    return render_template("register.html", role="Sponsor")

@app.route("/register/influencer", methods=["GET", "POST"])
def registerInfluencer():
    if request.method == "POST":
        pass

    return render_template("register.html", role="Influencer")


if __name__ == "__main__":
    app.run(port=8000, debug=True)