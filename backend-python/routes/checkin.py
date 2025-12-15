import sqlite3
import os
from openai import OpenAI
from datetime import datetime

# from .chat import get_openai_client

DB_PATH = "/Users/worktrial7/Documents/bevel-onsite/event_checkins.db"

async def save_checkin(structured_checkin):
    # Implement the logic to save the structured check-in to the database
    category = structured_checkin["category"]
    check_in_time = structured_checkin["check_in_time"]
    message_content = structured_checkin["message_content"]

    if not(category and check_in_time and message_content):
        print("Incomplete check-in data; not saving.")
        return
    
    try:
        # print("trying to save check-in to the database...")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # Insert the check-in
        cur.execute("""
            INSERT INTO event_checkins (message_content, check_in_time, category, created_at, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            message_content,
            check_in_time,                  # ISO format string: "2025-12-15T15:00:00"
            category,
            datetime.utcnow().isoformat(),  # created_at
            "active"                        # default status
        ))
        conn.commit()
        print("Check-in saved successfully.", message_content, check_in_time)
    except Exception as e:
        print(e)
        print("Error saving check-in to the database.")

def update_checkin(event_ids, action, updated_time=None, updated_message=None):
    """
    Update or delete a check-in based on action.
    action: "update" or "delete"
    If "update", updated_time should be provided (ISO format string).
    """
    try:
        print(f"Updating check-in {event_ids} with action {action}...")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        if not event_ids:
            print("No event IDs provided.")
            return

        ids = ",".join("?" for _ in event_ids)  # "?, ?, ?"

        if action == "delete":
            sql = f"""
                DELETE FROM event_checkins
                WHERE event_id IN ({ids})
            """
            cur.execute(sql, event_ids)

        elif action == "update" and updated_time:
            sql = f"""
                UPDATE event_checkins
                SET check_in_time = ?,
                    message_content = ?
                WHERE event_id IN ({ids})
            """
            cur.execute(sql, [updated_time, updated_message, *event_ids])
        else:
            print("Invalid action or missing updated_time for update.")
            return

        conn.commit()
        print("Check-in updated successfully.")
    except Exception as e:
        print(e)
        print("Error updating check-in in the database.")


