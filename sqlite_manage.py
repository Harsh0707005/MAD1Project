import sqlite3

connect = sqlite3.connect('users.db')
# connect.execute('ALTER Table users ADD COLUMN sessionId TEXT')
# connect.execute('DROP TABLE influencers')
# connect.execute('DROP TABLE sponsors')
# connect.execute('PRAGMA foreign_keys = ON;')
cursor = connect.cursor()

# cursor.execute("SELECT * FROM users")
# cursor.execute("DROP TABLE campaigns")
# cursor.execute("SELECT * FROM influencers")
# cursor.execute("DELETE FROM users WHERE username = 'abc' OR username = 'bcd'")
# cursor.execute("INSERT INTO campaigns (title, description, image, niche, sponsor, budget, date) values (?, ?, ?, ?, ?, ?, ?)", ('tes', 'ta', 'im', 'ca', 'bcd', 0, 'tate'))
# connect.commit()
# connect.commit()
# cursor.execute("SELECT * FROM users")
# cursor.execute('PRAGMA foreign_keys = ON;')
# cursor.execute('DELETE FROM users WHERE username =? ', ('test',))
# cursor.execute('PRAGMA foreign_key_list(influencers);')
# cursor.execute('INSERT INTO influencers (username, presence, profic_pic, requests, total_earnings, rating) VALUES(?, ?, ?, ?, ?, ?)', ('test2', "", "", "", 0, 0))


def copy():
    with sqlite3.connect('users.db') as conn1:
        cursor = conn1.cursor()
        conn1.execute('CREATE TABLE IF NOT EXISTS new_campaigns (id INTEGER NOT NULL PRIMARY KEY, title TEXT, description TEXT, image TEXT, niche TEXT, request_sent TEXT, request_received TEXT, influencer TEXT, sponsor TEXT, budget NUMERIC, completed INT, date TEXT)')
        conn1.commit()
        cursor.execute('INSERT INTO new_campaigns(id, title, description, image, niche, request_sent, request_received, influencer, sponsor, budget, date) SELECT id, title, description, image, niche, request_sent, request_received, influencer, sponsor, budget, date FROM campaigns')
        conn1.commit()
        cursor.execute('SELECT * FROM new_campaigns')
        print(cursor.fetchall())
        cursor.execute('SELECT * FROM campaigns')
        print(cursor.fetchall())
        cursor.execute('DROP TABLE campaigns')
        cursor.execute('ALTER TABLE new_campaigns RENAME TO campaigns')

cursor.execute('SELECT * FROM campaigns')

connect.commit()
print(cursor.fetchall())