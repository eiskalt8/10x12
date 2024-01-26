import sqlite3

days_until_delete_sessions = 7
days_until_delete_users = 30

conn = sqlite3.connect('10x12_Website.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM main.Sessions WHERE julianday('now') - julianday(last_used) > ?",
               (days_until_delete_sessions,))
cursor.execute("DELETE FROM main.Users WHERE julianday('now') - julianday(last_used) > ?", (days_until_delete_users,))

conn.commit()
cursor.close()
