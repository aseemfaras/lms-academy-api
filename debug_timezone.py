import sqlite3

conn = sqlite3.connect('C:/aideas/lms-backend/db.sqlite3')
cur = conn.cursor()

tables = [t[0] for t in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print(tables)

table_name = 'trainers_livesession' if 'trainers_livesession' in tables else 'live_sessions'

try:
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT id, title, scheduled_date, start_time, end_time FROM {table_name} WHERE title LIKE '%gen ai%' OR title LIKE '%neural%'")
    rows = cur.fetchall()
    print("DATA:")
    for r in rows:
        print(dict(r))
except Exception as e:
    print(f"Error querying {table_name}: {e}")
