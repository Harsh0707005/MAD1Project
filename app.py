from flask import Flask, render_template, request, url_for
import sqlite3

app = Flask(__name__)

connect = sqlite3.connect('users.db')
connect.execute('CREATE TABLE IF NOT EXISTS users (email TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)')

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass
    return render_template("login.html")

@app.route("/register/sponsor", methods=["GET", "POST"])
def registerSponsor():
    if request.method == "POST":

        role = "sponsor"
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template('register.html', errMessage = "Passwords do not match!", emailInput = email)

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            
            if cursor.fetchall():
                return render_template('register.html', errMessage = "User already exists!", emailInput=email)
            else:
                cursor.execute('INSERT INTO users(email, password, role) VALUES(?, ?, ?)', (email, password, role))
                users.commit()

                return cursor.execute("SELECT * FROM users").fetchall()

    return render_template("register.html", role="Sponsor")

@app.route("/register/influencer", methods=["GET", "POST"])
def registerInfluencer():
    if request.method == "POST":
        role = "influencer"
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template('register.html', errMessage = "Passwords do not match!", emailInput = email)
        
        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            
            if cursor.fetchall():
                return render_template('register.html', errMessage = "User already exists!", emailInput=email)
            else:
                cursor.execute('INSERT INTO users(email, password, role) VALUES(?, ?, ?)', (email, password, role))
                users.commit()
                return cursor.execute("SELECT * FROM users").fetchall()

    return render_template("register.html", role="Influencer")


if __name__ == "__main__":
    app.run(port=8000, debug=True)