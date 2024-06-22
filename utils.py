import string
import random
import sqlite3

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
    if query != None:
        query = "%" + query + "%"
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        if query:
            cursor.execute('SELECT * FROM campaigns WHERE title LIKE ? OR description LIKE ? OR niche LIKE ? ORDER BY date DESC', (query, query, query))
        else:
            cursor.execute('SELECT * FROM campaigns')
        data = cursor.fetchall()
        return data

def searchUsers(query, user):
    query = "%" + query + "%"
    if user[-1] != 's': user+='s'
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        cursor.execute(f"SELECT * FROM {user} WHERE username LIKE '{query}'")
        data = cursor.fetchall()
        return data

def getTableData(table, col=None, val=None):
    with sqlite3.connect('users.db') as users:
        cursor = users.cursor()
        if col and val:
            query = f'SELECT * FROM {table} WHERE {col} = ?'
            cursor.execute(query, (val,))
        else:
            query = f'SELECT * FROM {table}'
            cursor.execute(query)
        data = cursor.fetchall()
        return data