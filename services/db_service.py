# services/db_service.py

import duckdb
from pathlib import Path
from models.room import Room

DB_PATH = "chat.duckdb"


def get_connection():
    return duckdb.connect(DB_PATH)


def init_db():
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id         VARCHAR PRIMARY KEY,
            name       VARCHAR NOT NULL,
            created_by VARCHAR NOT NULL
        )
    """)
    result = con.execute("SELECT id FROM rooms WHERE name = 'Geral'").fetchone()
    if not result:
        con.execute("INSERT INTO rooms (id, name, created_by) VALUES (?, ?, ?)",
                    ["sala-geral", "Geral", "sistema"])
    con.close()


def get_all_rooms():
    con = get_connection()
    rows = con.execute("SELECT id, name, created_by FROM rooms ORDER BY name").fetchall()
    con.close()
    return [Room(id=row[0], name=row[1], created_by=row[2]) for row in rows]


def save_room(room: Room):
    con = get_connection()
    con.execute("INSERT INTO rooms (id, name, created_by) VALUES (?, ?, ?)",
                [room.id, room.name, room.created_by])
    con.close()


def room_exists(name: str) -> bool:
    con = get_connection()
    result = con.execute("SELECT id FROM rooms WHERE LOWER(name) = LOWER(?)", [name]).fetchone()
    con.close()
    return result is not None