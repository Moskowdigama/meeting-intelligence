import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class ActionTracker:
    def __init__(self, db_path: str = "data/meetings.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        import os
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY, title TEXT, date TEXT,
                    transcript TEXT, summary TEXT, created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id TEXT PRIMARY KEY, meeting_id TEXT, action TEXT,
                    assigned_to TEXT, deadline TEXT, priority TEXT,
                    status TEXT DEFAULT 'pending', created_at TEXT,
                    FOREIGN KEY (meeting_id) REFERENCES meetings(id)
                )
            """)
            conn.commit()
    
    def save_meeting(self, title: str, transcript: str, summary: str) -> str:
        meeting_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO meetings (id, title, date, transcript, summary, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (meeting_id, title, now, transcript, summary, now)
            )
            conn.commit()
        return meeting_id
    
    def save_action_items(self, meeting_id: str, actions: List[Dict[str, Any]]):
        with sqlite3.connect(self.db_path) as conn:
            for action in actions:
                conn.execute(
                    "INSERT INTO action_items (id, meeting_id, action, assigned_to, deadline, priority, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4())[:8], meeting_id, action.get("action", ""), action.get("assigned_to", "Unassigned"), action.get("deadline", "No deadline"), action.get("priority", "MEDIUM"), "pending", datetime.now().isoformat())
                )
            conn.commit()
    
    def get_meetings(self) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute("SELECT id, title, date, summary, created_at FROM meetings ORDER BY date DESC").fetchall()]
    
    def get_meeting(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM meetings WHERE id = ?", (meeting_id,)).fetchone()
        return dict(row) if row else None
    
    def get_action_items(self, meeting_id: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT a.*, m.title as meeting_title FROM action_items a JOIN meetings m ON a.meeting_id = m.id WHERE 1=1"
        params = []
        if meeting_id:
            query += " AND a.meeting_id = ?"
            params.append(meeting_id)
        if status:
            query += " AND a.status = ?"
            params.append(status)
        query += " ORDER BY a.created_at DESC"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(row) for row in conn.execute(query, params).fetchall()]
    
    def update_action_status(self, action_id: str, status: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE action_items SET status = ? WHERE id = ?", (status, action_id))
            conn.commit()
    
    def get_action_summary(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM action_items").fetchone()[0]
            pending = conn.execute("SELECT COUNT(*) FROM action_items WHERE status = 'pending'").fetchone()[0]
            done = conn.execute("SELECT COUNT(*) FROM action_items WHERE status = 'done'").fetchone()[0]
            by_priority = conn.execute("SELECT priority, COUNT(*) FROM action_items WHERE status = 'pending' GROUP BY priority").fetchall()
        return {
            "total": total,
            "pending": pending,
            "done": done,
            "by_priority": {row[0]: row[1] for row in by_priority}
        }
