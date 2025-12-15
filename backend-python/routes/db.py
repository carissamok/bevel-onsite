import sqlite3
import os
from datetime import datetime, timedelta
DB_PATH = "/Users/worktrial7/Documents/bevel-onsite/event_checkins.db"

conn = sqlite3.connect("event_checkins.db")
cur = conn.cursor()

# Create table
cur.execute("""
CREATE TABLE IF NOT EXISTS event_checkins (
  event_id INTEGER PRIMARY KEY AUTOINCREMENT,
  message_content TEXT NOT NULL,
  check_in_time TEXT NOT NULL,
  category TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  status TEXT DEFAULT 'active'
);
""")
conn.commit()

print("Database and table initialized.")
conn.close()

def get_active_checkins(days: int = 7):
  """
  Return list of active check-ins from the last `days` days.
  Each item is a dict with keys: message_content, check_in_time, category, created_at, status.
  """
  db_path = os.path.abspath(DB_PATH)
  conn = sqlite3.connect(db_path)
  conn.row_factory = sqlite3.Row
  cur = conn.cursor()

  query = """
  select * from event_checkins 
  where datetime(replace(substr(created_at, 1, 19), 'T', ' ')) >= ?;
  """

  cutoff = datetime.utcnow() - timedelta(days=days)
  cutoff_str = cutoff.strftime('%Y-%m-%d %H:%M:%S')

  cur.execute(query, (cutoff_str,))
 
  rows = cur.fetchall()
  results = []
  for r in rows:
    results.append({
      "event_id": r["event_id"],
      "message_content": r["message_content"],
      "check_in_time": r["check_in_time"],
      "category": r["category"],
      "created_at": r["created_at"],
      "status": r["status"],
    })
  conn.close()
  return results
