# models/room.py

from dataclasses import dataclass, field
import uuid


@dataclass
class Room:
    """
    Representa uma sala de chat.

    Atributos:
        name       - o nome da sala (ex: "Geral", "Jogos")
        id         - identificador único gerado automaticamente
        created_by - o username de quem criou a sala
    """
    name: str
    created_by: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))