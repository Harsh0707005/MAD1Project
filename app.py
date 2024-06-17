from flask import Flask, render_template, request, url_for, make_response
import sqlite3
import string
import random

app = Flask(__name__)

connect = sqlite3.connect('users.db')
connect.execute('CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL)')

# generating random session id
def generateRandomNo(n):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username == "" or password == "":
            return render_template('login.html', errMessage = "Please fill in all fields!", usernameInput = username)

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users where username = ?', (username,))

            db_res = cursor.fetchone()

            if db_res:
                if db_res[2] == "admin":
                    return render_template('login.html', role="User" , errMessage = "Login as admin!")
                elif password == db_res[1]:
                    sessionId = generateRandomNo(30)
                    response = make_response(render_template('login.html', role="User", errMessage = "Login Successful!"))
                    response.set_cookie("sessionId", sessionId)
                    return response
                else:
                    return render_template('login.html', role="User" , usernameInput = username, errMessage = "Invalid Password!")
                
            else:
                return render_template('login.html', role="User" , errMessage = "User doesn't exist!")

    return render_template("login.html", role="User")

@app.route("/login/admin", methods=['GET', 'POST'])
def admin():
    if request.method == "POST":
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if username == "" or password == "":
            return render_template('login.html', role="Admin", errMessage = "Please fill in all fields!", usernameInput = username)

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users where username = ?', (username,))

            db_res = cursor.fetchone()

            if db_res:
                if db_res[2] == "admin":
                    if password == db_res[1]:
                        return render_template('login.html', role="Admin" , errMessage = "Login Successful!")
                    else:
                        return render_template('login.html', role="Admin" , usernameInput = username, errMessage = "Invalid Password!")
                else:
                    return render_template('login.html', role="Admin" , errMessage = "No Admin Users Found!")
            else:
                return render_template('login.html', role="Admin" , errMessage = "User doesn't exist!")

    return render_template('login.html', role="Admin")


@app.route("/register/sponsor", methods=["GET", "POST"])
def registerSponsor():
    if request.method == "POST":

        role = "sponsor"
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"]

        if username == "" or password == "":
            return render_template('register.html', role="Sponsor" , errMessage = "Please fill in all fields!", usernameInput = username)

        if password != confirm_password:
            return render_template('register.html', role="Sponsor" , errMessage = "Passwords do not match!", usernameInput = username)

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            
            if cursor.fetchall():
                return render_template('register.html', role="Sponsor" , errMessage = "User already exists!", usernameInput=username)
            else:
                cursor.execute('INSERT INTO users(username, password, role) VALUES(?, ?, ?)', (username, password, role))
                users.commit()

                return cursor.execute("SELECT * FROM users").fetchall()

    return render_template("register.html", role="Sponsor")

@app.route("/register/influencer", methods=["GET", "POST"])
def registerInfluencer():
    if request.method == "POST":
        role = "influencer"
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        confirm_password = request.form["confirm_password"].strip()

        if username == "" or password == "" or confirm_password == "":
            return render_template('register.html', role="Influencer" , errMessage = "Please fill in all fields!", usernameInput = username)

        if password != confirm_password:
            return render_template('register.html', role="Influencer" , errMessage = "Passwords do not match!", usernameInput = username)
        
        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()

            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            
            if cursor.fetchall():
                return render_template('register.html', role="Influencer" , errMessage = "User already exists!", usernameInput=username)
            else:
                cursor.execute('INSERT INTO users(username, password, role) VALUES(?, ?, ?)', (username, password, role))
                users.commit()
                return cursor.execute("SELECT * FROM users").fetchall()

    return render_template("register.html", role="Influencer")


if __name__ == "__main__":
    app.run(port=8000, debug=True)