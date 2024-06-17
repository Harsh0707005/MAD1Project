import sqlite3

connect = sqlite3.connect('users.db')
# connect.execute('ALTER Table users ADD COLUMN sessionId TEXT')
cursor = connect.cursor()

cursor.execute("SELECT * FROM users")
print(cursor.fetchall())