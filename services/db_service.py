# services/db_service.py

import duckdb
import os
from models.room import Room

# Caminho para o ficheiro da base de dados
# Fica na raiz do projeto
DB_PATH = "chat.duckdb"


def get_connection():
    """
    Cria e devolve uma ligação ao DuckDB.
    Cada chamada abre uma ligação nova — o DuckDB gere isto eficientemente.
    """
    return duckdb.connect(DB_PATH)


def init_db():
    """
    Cria as tabelas na base de dados se ainda não existirem.
    Esta função é chamada uma vez quando a app arranca.
    """
    con = get_connection()

    # Tabela de salas
    con.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id         VARCHAR PRIMARY KEY,
            name       VARCHAR NOT NULL,
            created_by VARCHAR NOT NULL
        )
    """)

    # Verifica se a sala "Geral" já existe, se não cria-a
    result = con.execute(
        "SELECT id FROM rooms WHERE name = 'Geral'"
    ).fetchone()

    if not result:
        con.execute("""
            INSERT INTO rooms (id, name, created_by)
            VALUES (?, ?, ?)
        """, ["sala-geral", "Geral", "sistema"])

    con.close()


def get_all_rooms():
    """
    Devolve todas as salas guardadas na base de dados.
    Retorna uma lista de objetos Room.
    """
    con = get_connection()
    rows = con.execute(
        "SELECT id, name, created_by FROM rooms ORDER BY name"
    ).fetchall()
    con.close()

    return [Room(id=row[0], name=row[1], created_by=row[2]) for row in rows]


def save_room(room: Room):
    """
    Guarda uma sala nova na base de dados.
    """
    con = get_connection()
    con.execute("""
        INSERT INTO rooms (id, name, created_by)
        VALUES (?, ?, ?)
    """, [room.id, room.name, room.created_by])
    con.close()


def room_exists(name: str) -> bool:
    """
    Verifica se já existe uma sala com este nome.
    Usado para evitar salas duplicadas.
    """
    con = get_connection()
    result = con.execute(
        "SELECT id FROM rooms WHERE LOWER(name) = LOWER(?)", [name]
    ).fetchone()
    con.close()
    return result is not None