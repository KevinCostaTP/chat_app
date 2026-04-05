# models/room.py

from dataclasses import dataclass, field
import uuid


@dataclass
class Room:
    name: str
    created_by: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))