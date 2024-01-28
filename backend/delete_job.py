import sqlite3

days_until_delete_sessions = 7
days_until_delete_users = 10

conn = sqlite3.connect('/var/www/10x12/backend/10x12_lite.db')
cursor = conn.cursor()

cursor.execute("DELETE FROM Sessions WHERE julianday('now') - julianday(last_used) > ?",
               (days_until_delete_sessions,))
cursor.execute("DELETE FROM Users WHERE julianday('now') - julianday(last_used) > ?", (days_until_delete_users,))

conn.commit()
cursor.close()
