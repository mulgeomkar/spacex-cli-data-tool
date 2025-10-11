import sqlite3
from typing import List, Dict, Any
from models import Launch

class SpaceXDatabase:
    def __init__(self, db_path: str = "spacex.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS launches (
                id TEXT PRIMARY KEY,
                flight_number INTEGER UNIQUE,
                name TEXT,
                date_utc TEXT,
                success BOOLEAN,
                details TEXT,
                rocket TEXT,
                launchpad TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_launches_success ON launches(success)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_launches_rocket ON launches(rocket)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_launches_date ON launches(date_utc)')
        conn.commit()
        conn.close()

    def insert_launches(self, launches: List[Launch]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Insert launches, ignore duplicates
        for l in launches:
            cursor.execute('''
                INSERT OR IGNORE INTO launches (
                    id, flight_number, name, date_utc, success, details, rocket, launchpad
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                l.id, l.flight_number, l.name, l.date_utc, int(l.success) if isinstance(l.success, bool) else None,
                l.details, l.rocket, l.launchpad
            ))
        conn.commit()
        conn.close()

    def query_launches(self, filters: Dict[str, Any], limit: int = 5) -> List[Launch]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = "SELECT id, flight_number, name, date_utc, success, details, rocket, launchpad FROM launches"
        params, where = [], []
        for k, v in filters.items():
            where.append(f"{k} = ?")
            params.append(v if not isinstance(v, bool) else int(v))
        if where:
            query += " WHERE " + " AND ".join(where)
        query += " ORDER BY flight_number DESC LIMIT ?"
        params.append(limit)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        result = []
        for r in rows:
            result.append(Launch(
                id=r[0], flight_number=r[1], name=r[2], date_utc=r[3],
                success=bool(r[4]) if r[4] is not None else None, details=r[5],
                rocket=r[6], launchpad=r[7]
            ))
        return result
