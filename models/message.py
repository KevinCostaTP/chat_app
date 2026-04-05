# models/message.py

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    username: str
    text: str
    room_id: str = "geral"
    msg_type: str = "chat"  # chat, login, edit, delete, react, sticker
    file_path: str = None
    is_edited: bool = False
    is_deleted: bool = False
    reactions: dict = field(default_factory=dict)  # {emoji: [username, ...]}
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)