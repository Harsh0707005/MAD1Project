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


def copy_campaigns():
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

def copy_influencers():
    with sqlite3.connect('users.db') as conn1:
        cursor = conn1.cursor()
        cursor.execute('DROP TABLE new_influencers')
        conn1.commit()
        conn1.execute('CREATE TABLE IF NOT EXISTS new_influencers (username TEXT NOT NULL, presence TEXT, profile_pic TEXT, request_sent TEXT, request_received TEXT, total_earnings NUMERIC, rating NUMERIC, requested_campaigns INTEGER, assigned_campaigns INTEGER, completed_campaigns INTEGER, "1star" INTEGER, "2star" INTEGER, "3star" INTEGER, "4star" INTEGER, "5star" INTEGER, FOREIGN KEY(username) REFERENCES users(username) ON DELETE CASCADE)')

        cursor.execute('INSERT INTO new_influencers(username, presence, profile_pic, request_sent, request_received, total_earnings, rating) SELECT username, presence, profile_pic, request_sent, request_received, total_earnings, rating FROM influencers')

        conn1.commit()
        cursor.execute('SELECT * FROM new_influencers')
        print(cursor.fetchall())
        cursor.execute('SELECT * FROM influencers')
        print(cursor.fetchall())
        cursor.execute('DROP TABLE influencers')
        cursor.execute('ALTER TABLE new_influencers RENAME TO influencers')

cursor.execute('SELECT * FROM influencers')
connect.commit()
print(cursor.fetchall())