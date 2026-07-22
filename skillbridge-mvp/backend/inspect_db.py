import os
import sqlite3

path = r"C:/Users/sovit/Hackathon-2026/skillbridge-mvp/backend/skillbridge.db"
conn = sqlite3.connect(path)
cur = conn.cursor()
print('exists', os.path.exists(path))
print('tables', cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall())
print('lessons_count', cur.execute('SELECT COUNT(*) FROM lessons').fetchone()[0])
print('profiles_count', cur.execute('SELECT COUNT(*) FROM profiles').fetchone()[0])
print('users_count', cur.execute('SELECT COUNT(*) FROM users').fetchone()[0])
print('profile_rows', cur.execute('SELECT user_id, target_role, current_level FROM profiles').fetchall())
conn.close()
