import sqlite3

# connect to Database / create it
conn = sqlite3.connect('10x12_lite.db')
cursor = conn.cursor()

# create Tables Users and Sessions
cursor.execute("CREATE TABLE IF NOT EXISTS Users (UserID INTEGER PRIMARY KEY, UserName VARCHAR(20), last_used DATE)")
cursor.execute("CREATE TABLE IF NOT EXISTS Sessions (SessionID INTEGER PRIMARY KEY, Users TEXT, last_used DATE)")

# execute and close
conn.commit()
conn.close()
