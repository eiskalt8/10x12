import sqlite3

# connect to Database / create it
conn = sqlite3.connect('10x12_lite.db')
cursor = conn.cursor()

# create Tables Users and Sessions
cursor.execute("CREATE TABLE IF NOT EXISTS Users (UserID CHAR(36) PRIMARY KEY, UserName VARCHAR(20), last_used DATE)")
cursor.execute("CREATE TABLE IF NOT EXISTS Sessions (SessionID INTEGER PRIMARY KEY, Users TEXT, last_used DATE, "
               "locked BOOLEAN DEFAULT 0, current_player CHAR(36))")

# execute and close
conn.commit()
conn.close()
