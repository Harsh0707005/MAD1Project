import string
import random
import sqlite3

# generating random session id
def generateRandomNo(n):
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(n))

def checkSessionId(sessionId):
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM users WHERE sessionId=?', (sessionId,))
        return cursor.fetchone()

def getRole(sessionId):
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT role FROM users WHERE sessionId=?', (sessionId,))
        return cursor.fetchone()[0].title()

def searchCampaigns(query):
    query = "%" + query + "%"
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE title LIKE ? OR description LIKE ? OR niche LIKE ?', (query, query, query))
        data = cursor.fetchall()
        return data

def searchUsers(query, user):
    query = "%" + query + "%"
    user+='s'
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute('SELECT * FROM ? WHERE username LIKE ?', (user, query))
        data = cursor.fetchall()
        return data