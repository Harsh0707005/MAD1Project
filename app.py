from flask import Flask, render_template, request, url_for, make_response, redirect
import sqlite3
import json
from datetime import datetime
import utils


app = Flask(__name__)

connect = sqlite3.connect('users.db')
connect.execute('PRAGMA foreign_keys = ON;')
connect.execute('CREATE TABLE IF NOT EXISTS users (username TEXT NOT NULL PRIMARY KEY, password TEXT NOT NULL, role TEXT NOT NULL, sessionId TEXT)')
connect.execute('CREATE TABLE IF NOT EXISTS influencers (username TEXT NOT NULL, presence TEXT, profile_pic TEXT, request_sent TEXT, request_received TEXT, total_earnings NUMERIC, rating INTEGER, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE)')
connect.execute('CREATE TABLE IF NOT EXISTS sponsors (username TEXT NOT NULL, industry TEXT, requests TEXT, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE)')
connect.execute('CREATE TABLE IF NOT EXISTS campaigns (id INTEGER NOT NULL PRIMARY KEY, title TEXT, description TEXT, image TEXT, niche TEXT, request_sent TEXT, request_received TEXT, influencer TEXT, sponsor TEXT, budget NUMERIC, date TEXT)')

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
                    sessionId = utils.generateRandomNo(30)
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
                # cursor.execute('INSERT INTO influencers(username, presence, profic_pic, requests, total_earnings, rating) VALUES(?, ?, ?, ?, ?, ?)', (username, "", "", "", 0, 0))
                cursor.execute('INSERT INTO influencers(username, presence, profile_pic, request_sent, request_received, total_earnings, rating) VALUES(?, ?, ?, ?, ?, ?, ?)', (username, "", "", "", "", 0, 0))
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
        requests_campaigns, active_campaigns = [], []
        if user_role == 'Sponsor':
            cursor.execute('SELECT * FROM campaigns WHERE sponsor=? AND request_received IS NOT NULL', (db_username,))
            requests_campaigns = cursor.fetchall()
            cursor.execute('SELECT * FROM campaigns WHERE sponsor=? AND completed!=1', (db_username,))
            active_campaigns = cursor.fetchall()
        elif user_role == 'Influencer':
            cursor.execute('SELECT * FROM campaigns WHERE influencer=?', (db_username,))
            active_campaigns = cursor.fetchall()
            cursor.execute('SELECT * FROM campaigns WHERE request_sent LIKE ?', ('%' + db_username + '%',))
            requests_campaigns = cursor.fetchall()

    return render_template('dashboard/profile.html', role=user_role, username=db_username, active_campaigns=active_campaigns, requests_campaigns=requests_campaigns)

@app.route("/find", methods=['GET'])
def find():
    # role = utils.getRole(request.cookies.get("sessionId"))
    # data = utils.searchCampaigns(None)
    # return render_template('dashboard/find.html', data=data, role=role, resultFor='campaigns')
    return redirect('/find/campaigns')

@app.route('/find/campaigns', methods=['GET'])
def find_campaigns():
    if request.args.get('q'):
        search_query = "%" + request.args.get('q') + "%"
    else:
        search_query = False
    role = utils.getRole(request.cookies.get("sessionId"))
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        if search_query == False:
            cursor.execute('SELECT * FROM campaigns ORDER BY date DESC')
            campaigns = cursor.fetchall()
        else:
            campaigns = utils.searchCampaigns(search_query)
        return render_template('dashboard/find.html', data=campaigns, role=role, resultFor="campaigns")
    
@app.route('/find/influencers', methods=['GET'])
def find_influencers():
    if request.args.get('q'):
        search_query = "%" + request.args.get('q') + "%"
    else:
        search_query = False
    role = utils.getRole(request.cookies.get("sessionId"))
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        if search_query == False:
            cursor.execute('SELECT * FROM influencers')
            influencers = cursor.fetchall()
        else:
            influencers = utils.searchUsers(search_query, "influencer")
        return render_template('dashboard/find.html', data=influencers, role=role, resultFor="influencers")

@app.route("/search/<resultFor>", methods=['POST'])
def search(resultFor):
    role = utils.getRole(request.cookies.get("sessionId"))
    if resultFor=="campaigns":
        data = utils.searchCampaigns(request.args.get('q'))
    else:
        data = utils.searchUsers(request.args.get('q'), resultFor)
    
    return render_template('/dashboard/processSearchResults.html', data=data, resultFor=resultFor, role=role)

@app.route("/request", methods=['POST'])
def request_campaign():
    user_data = utils.checkSessionId(request.cookies.get("sessionId"))
    if user_data == None:
        return redirect("/login")
    username = user_data[0]
    role = utils.getRole(request.cookies.get("sessionId"))
    request_data = request.get_json()
    campaign_id = request_data['campaign_id']

    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id=?', (campaign_id,))
        campaign_data = cursor.fetchone()
        if not campaign_data:
            response = make_response('Campaign not found')
            response.status_code = 404
            return response
        cursor.execute('SELECT request_sent FROM influencers WHERE username=?', (username,))
        influencer_request_sent = cursor.fetchone()
        if not influencer_request_sent:
            response = make_response('Influencer not found')
            response.status_code = 404
            return response
        
        if influencer_request_sent==(None,):
            new_influencer_request_sent = campaign_id
        else:
            if campaign_id in influencer_request_sent[0].split(","):
                response = make_response('Request already sent')
                response.status_code = 400
                return response
            
            new_influencer_request_sent = influencer_request_sent[0] + "," + campaign_id

        # cursor.execute('UPDATE influencers SET request_sent=? WHERE username=?', (new_influencer_request_sent, username))
        cursor.execute('SELECT request_received FROM campaigns WHERE id=?', (campaign_id,))
        request_received = cursor.fetchone()
        if request_received[0] == None:
            new_request_received = username
        else:
            new_request_received = request_received[0] + "," + username

        cursor.executescript(f'''
UPDATE influencers SET request_sent="{new_influencer_request_sent}" WHERE username="{username}";
UPDATE campaigns SET request_received="{new_request_received}" WHERE id="{campaign_id}";
                             ''')
        users.commit()
        # print(utils.getTableData('influencers', col='username', val=username))
        # print(utils.getTableData('campaigns', col='id', val=campaign_id))

    return ""

@app.route("/request/influencer/<influencer>/<campaign_id>", methods=['GET'])
def request_influencer(influencer, campaign_id):
    user_data = utils.checkSessionId(request.cookies.get("sessionId"))
    if user_data == None:
        return redirect("/login")
    username = user_data[0]
    role = utils.getRole(request.cookies.get("sessionId"))
    if role.lower() == 'influencer':
        response = make_response('Access Denied')
        response.status_code = 403
        return response
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id=?', (campaign_id,))
        campaign_data = cursor.fetchone()
        if not campaign_data:
            response = make_response('Campaign not found')
            response.status_code = 404
            return response
        
        if campaign_data[7] == None or campaign_data[7].strip() == "":
            new_request_sent = influencer
        else:
            new_request_sent = campaign_data[5] + "," + influencer
        
        cursor.execute('SELECT request_received FROM influencers WHERE username=?', (influencer,))
        influencer_request_received = cursor.fetchone()
        if not influencer_request_received:
            response = make_response('Influencer not found')
            response.status_code = 404
            return response
        if (influencer_request_received[0] == None or influencer_request_received[0].strip() == ""):
            new_influencer_request_received = campaign_id
        else:
            new_influencer_request_received = influencer_request_received[0] + "," + campaign_id

        cursor.executescript(f'''
UPDATE influencers SET request_received="{new_influencer_request_received}" WHERE username="{influencer}";
UPDATE campaigns SET request_sent="{new_request_sent}" WHERE id="{campaign_id}";
                             ''')
        users.commit()
        return ""

@app.route("/<influencer>/accept_campaign/<campaign_id>", methods=['GET'])
def accept_influencer(influencer, campaign_id):
    user_data = utils.checkSessionId(request.cookies.get("sessionId"))
    if user_data == None:
        return redirect("/login")
    username = user_data[0]
    role = utils.getRole(request.cookies.get("sessionId"))
    if role.lower() == 'influencer':

        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT request_sent FROM campaigns WHERE id=?', (campaign_id))
            request_sent = cursor.fetchone()[0].split(",")
            if request_sent != (None,) and (username in request_sent):

                cursor.execute('UPDATE campaigns SET request_received=NULL WHERE id=?', (campaign_id,))
                cursor.execute('UPDATE campaigns SET request_sent=NULL WHERE id=?', (campaign_id,))
                cursor.execute('UPDATE campaigns SET influencer=? WHERE id=?', (username, campaign_id))
                cursor.execute('SELECT request_received FROM influencers WHERE username=?', (username,))
                request_received = cursor.fetchone()[0].split(",")
                if request_received != (None,) and (campaign_id in request_received):
                    request_received.remove(campaign_id)
                    new_request_received = ",".join(request_received)
                    cursor.execute('UPDATE influencers SET request_received=? WHERE username=?', (new_request_received, username))
                users.commit()
        return ""

    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT request_received FROM campaigns WHERE id=? AND sponsor=?', (campaign_id,username))
        request_received = cursor.fetchone()[0].split(",")
        if request_received != (None,) and (influencer in request_received):
            cursor.execute('UPDATE campaigns SET request_received=NULL WHERE id=?', (campaign_id,))
            cursor.execute('UPDATE campaigns SET influencer=? WHERE id=?', (influencer, campaign_id))
            cursor.execute('SELECT request_sent FROM influencers WHERE username=?', (influencer,))
            request_sent = cursor.fetchone()[0].split(",")
            if request_sent != (None,) and (campaign_id in request_sent):
                request_sent.remove(campaign_id)
                new_request_sent = ",".join(request_sent)
                cursor.execute('UPDATE influencers SET request_sent=? WHERE username=?', (new_request_sent, influencer))
            users.commit()
        return ""

@app.route("/<influencer>/reject_campaign/<campaign_id>", methods=['GET'])
def reject_influencer(influencer, campaign_id):
    user_data = utils.checkSessionId(request.cookies.get("sessionId"))
    if user_data == None:
        return redirect("/login")
    username = user_data[0]
    role = utils.getRole(request.cookies.get("sessionId"))
    if role.lower() == 'influencer':
        
        with sqlite3.connect('users.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT request_sent FROM campaigns WHERE id=?', (campaign_id))
            request_sent = cursor.fetchone()[0].split(",")
            if request_sent != (None,) and (username in request_sent):
                request_sent.remove(username)
                if request_sent == []:
                    cursor.execute('UPDATE campaigns SET request_sent=NULL WHERE id=?', (campaign_id))
                else:
                    new_request_sent = ",".join(request_sent)
                    cursor.execute('UPDATE campaigns SET request_sent=? WHERE id=?', (new_request_sent, campaign_id))
                cursor.execute('SELECT request_received FROM influencers WHERE username=?', (username,))
                request_received = cursor.fetchone()[0].split(",")
                if request_received != (None,) and (campaign_id in request_received):
                    request_received.remove(campaign_id)
                    new_request_received = ",".join(request_received)
                    cursor.execute('UPDATE influencers SET request_received=? WHERE username=?', (new_request_received, username))
                users.commit()

        return ""
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT request_received FROM campaigns WHERE id=? AND sponsor=?', (campaign_id,username))
        request_received = cursor.fetchone()[0].split(",")
        if request_received != (None,) and (influencer in request_received):
            request_received.remove(influencer)
            if request_received == []:
                cursor.execute('UPDATE campaigns SET request_received=NULL WHERE id=?', (campaign_id))
            else:
                new_request_received = ",".join(request_received)
                cursor.execute('UPDATE campaigns SET request_received=? WHERE id=?', (new_request_received, campaign_id))
            cursor.execute('SELECT request_sent FROM influencers WHERE username=?', (influencer,))
            request_sent = cursor.fetchone()[0].split(",")
            if request_sent != (None,) and (campaign_id in request_sent):
                request_sent.remove(campaign_id)
                new_request_sent = ",".join(request_sent)
                cursor.execute('UPDATE influencers SET request_sent=? WHERE username=?', (new_request_sent, influencer))
            users.commit()
        return ""

@app.route("/campaigns", methods=['GET'])
def campaigns():
    sessionId = request.cookies.get("sessionId")
    data = utils.checkSessionId(sessionId)
    if data == None:
        return redirect("/login")
    username = data[0]
    role = data[2].title()
    if role.lower() == 'influencer':
        response = make_response('Access Denied')
        response.status_code = 403
        return response
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE sponsor=? ORDER BY date DESC', (username,))
        campaigns = cursor.fetchall()
        return render_template('dashboard/campaigns.html', role=role, campaigns=campaigns)

@app.route("/campaigns/create", methods=['POST'])
def create_campaign():
    sessionId = request.cookies.get("sessionId")
    data = utils.checkSessionId(sessionId)
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
        # request_sent TEXT, request_received TEXT, influencer TEXT, sponsor TEXT, budget NUMERIC, date TEXT
        cursor.execute('INSERT INTO campaigns (title, description, image, niche, request_sent, request_received, influencer, sponsor, budget, completed, date) values (?, ?, ?, ?, NULL, NULL, NULL, ?, ?, ?, ?)', (campaign_title, campaign_description, campaign_image, campaign_niche, username, campaign_budget, 0, datenow))
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

@app.route("/unassignedCampaigns", methods=['GET', 'POST'])
def unassignedCampaigns():
    sessionId = request.cookies.get("sessionId")
    data = utils.checkSessionId(sessionId)
    role = utils.getRole(sessionId)
    username = data[0]
    if role.lower() == "influencer":
        response = make_response('Access Denied')
        response.status_code = 403
        return response
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE influencer IS NULL AND sponsor=? ORDER BY date DESC', (username,))
        campaigns = cursor.fetchall()
        return render_template('dashboard/assignCampaign.html', unassignedCampaigns=campaigns)

@app.route('/campaigns/<campaign_id>', methods=['GET'])
def getCampaign(campaign_id):
    data = utils.checkSessionId(request.cookies.get("sessionId"))
    role = utils.getRole(request.cookies.get("sessionId"))
    if data == None:
        return redirect("/login")
    
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id=?', (campaign_id,))
        data = cursor.fetchone()
        if data:
            return render_template('dashboard/processViewCampaign.html', campaign_data = data, role=role)
        else:
            response = make_response()
            response.status_code = 404
        return response

@app.route('/campaigns/<campaign_id>/mark-complete', methods=['GET'])
def markComplete(campaign_id):
    data = utils.checkSessionId(request.cookies.get("sessionId"))
    role = utils.getRole(request.cookies.get("sessionId"))
    if data == None:
        return redirect("/login")
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('UPDATE campaigns SET completed=? WHERE id=?', (1, campaign_id))
        users.commit()
        response = make_response()
        response.status_code = 200
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