import sqlite3
import json

conn = sqlite3.connect('C:/aideas/lms-backend/db.sqlite3')
cur = conn.cursor()
cur.execute('SELECT id, scheduled_date, start_time, end_time, status FROM trainers_livesession LIMIT 5')
rows = cur.fetchall()
print(json.dumps(rows, indent=2))
