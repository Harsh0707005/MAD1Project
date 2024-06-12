from flask import Flask, render_template, request, url_for
import sqlite3

app = Flask(__name__)

connect = sqlite3.connect('users.db')
connect.execute('CREATE TABLE IF NOT EXISTS users (email TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)')

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if email == "" or password == "":
            return render_template('login.html', errMessage = "Please fill in all fields!", emailInput = email)

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users where email = ?', (email,))

            db_res = cursor.fetchone()

            if db_res:
                if password == db_res[1]:
                    return render_template('login.html', errMessage = "Login Successful!")
                else:
                    return render_template('login.html', emailInput = email, errMessage = "Invalid Password!")
                
            else:
                return render_template('login.html', errMessage = "User doesn't exist!")

    return render_template("login.html")

@app.route("/register/sponsor", methods=["GET", "POST"])
def registerSponsor():
    if request.method == "POST":

        role = "sponsor"
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"]

        if email == "" or password == "":
            return render_template('register.html', errMessage = "Please fill in all fields!", emailInput = email)

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
        email = request.form["email"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        if email == "" or password == "" or confirm_password == "":
            return render_template('register.html', errMessage = "Please fill in all fields!", emailInput = email)

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