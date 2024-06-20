from flask import Flask, render_template, request, url_for, make_response, redirect
import sqlite3
import string
import random
import json
from datetime import datetime

app = Flask(__name__)

connect = sqlite3.connect('users.db')
connect.execute('PRAGMA foreign_keys = ON;')
connect.execute('CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL, sessionId TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS influencers (username TEXT NOT NULL, presence TEXT, profic_pic TEXT NOT NULL, requests TEXT, total_earnings NUMERIC, rating INTEGER, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE)')
connect.execute('CREATE TABLE IF NOT EXISTS sponsors (username TEXT NOT NULL, industry TEXT, requests TEXT, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE)')
connect.execute('CREATE TABLE IF NOT EXISTS campaigns (id INTEGER NOT NULL PRIMARY KEY, title TEXT, description TEXT, image TEXT, niche TEXT, influencer TEXT, sponsor TEXT, budget NUMERIC, date TEXT)')

# generating random session id
def generateRandomNo(n):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def checkSessionId(sessionId):
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM users WHERE sessionId=?', (sessionId,))
        return cursor.fetchone()

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET" and request.cookies.get("sessionId"):
        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT * FROM users WHERE sessionId=?', (request.cookies.get("sessionId"),))

            # print(cursor.fetchone())
            if cursor.fetchone():
                return redirect("/dashboard")
            else:
                response = make_response(render_template('login.html', role="User"))
                response.set_cookie("sessionId", "", max_age=0)
                return response
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
                    cursor.execute('UPDATE users SET sessionID=? WHERE username=?', (sessionId, username))
                    users.commit()
                    response = make_response(redirect("/dashboard"))
                    response.set_cookie("sessionId", sessionId, max_age=(60*60*24*7))
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
                cursor.execute('INSERT INTO sponsors(username, industry, requests) VALUES(?, ?, ?)', (username, "", ""))
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
                cursor.execute('INSERT INTO influencers(username, presence, profic_pic, requests, total_earnings, rating) VALUES(?, ?, ?, ?, ?, ?)', (username, "", "", "", 0, 0))
                return cursor.execute("SELECT * FROM users").fetchall()

    return render_template("register.html", role="Influencer")

@app.route("/dashboard", methods=['GET'])
@app.route("/profile", methods=['GET'])
def dashboard():
    sessionId = request.cookies.get("sessionId")
    # If session id absent or ""
    if sessionId == None or sessionId == "":
        return redirect("/login")
    else:
        # If session id present
        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT * FROM users WHERE sessionId=?', (sessionId,))
            db_result = cursor.fetchone()
            if db_result == [] or db_result == None:
                response = make_response(redirect("/login"))
                return response
            
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM users WHERE sessionId=?', (sessionId,))
        db_result = cursor.fetchone()
        user_role = db_result[2].title()
        db_username = db_result[0]
    
    return render_template('dashboard/profile.html', role=user_role, username=db_username, active_campaigns=[["test1"], ["test2"], ["test3"]], requests_campaigns=[["test1"], ["test2"], ["test3"]])

@app.route("/find", methods=['GET'])
def find():
    return render_template('dashboard/find.html', role="Influencer")

@app.route("/search", methods=['POST'])
def search():
    search_query = json.loads(request.data.decode('utf-8'))['query']
    return json.dumps(search_query)

@app.route("/campaigns", methods=['GET'])
def campaigns():
    sessionId = request.cookies.get("sessionId")
    data = checkSessionId(sessionId)
    if data == None:
        return redirect("/login")
    username = data[0]
    role = data[2].title()
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE sponsor=? ORDER BY date DESC', (username,))
        campaigns = cursor.fetchall()
        return render_template('dashboard/campaigns.html', role=role, campaigns=campaigns)

@app.route("/campaigns/create", methods=['POST'])
def create_campaign():
    sessionId = request.cookies.get("sessionId")
    data = checkSessionId(sessionId)
    if data == None:
        return redirect("/login")
    username = data[0]
    role = data[2].title()
    campaign_title = request.form['title']
    campaign_description = request.form['description']
    campaign_image = request.form['image']
    campaign_niche = request.form['niche']
    campaign_budget = request.form['budget']
    datenow = datetime.now()
    with sqlite3.connect('users.db')  as users:
        cursor = users.cursor()
        cursor.execute('INSERT INTO campaigns (title, description, image, niche, sponsor, budget, date) values (?, ?, ?, ?, ?, ?, ?)', (campaign_title, campaign_description, campaign_image, campaign_niche, username, campaign_budget, datenow))
        try:
            users.commit()
            creation_status = 201
        except Exception as e:
            creation_status = 400
        
        cursor.execute('SELECT * FROM campaigns WHERE sponsor=?', (username,))
        campaigns = cursor.fetchall()
        
        response = make_response(json.dumps(campaigns))
        response.status_code = creation_status
        response.headers['Content-Type'] = 'application/json'
        return response
    
@app.route("/processCampaigns", methods=['GET'])
def process():
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns ORDER BY date DESC')
        campaigns = cursor.fetchall()
        return render_template('dashboard/processCampaigns.html', campaigns=campaigns)


@app.route('/campaigns/<campaign_id>', methods=['GET'])
def getCampaign(campaign_id):
    data = checkSessionId(request.cookies.get("sessionId"))
    if data == None:
        return redirect("/login")
    
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id=?', (campaign_id,))
        data = cursor.fetchone()
        if data:
            return render_template('dashboard/processViewCampaign.html', campaign_data = data)
        else:
            response = make_response()
            response.status_code = 404
        return response

@app.route("/logout", methods=['GET'])
def logout():
    sessionId = request.cookies.get("sessionId")
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('UPDATE users SET sessionId=? WHERE sessionId=?', ("", sessionId))
        users.commit()
        response = make_response(redirect("/login"))
        response.set_cookie("sessionId", "", max_age=0)
        return response

if __name__ == "__main__":
    app.run(port=8000, debug=True)