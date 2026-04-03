# models/message.py

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """
    Representa uma mensagem enviada no chat.

    Atributos:
        username  - quem enviou
        text      - conteúdo de texto (pode ser vazio se for só ficheiro)
        room_id   - sala ou tópico privado
        msg_type  - "chat" ou "login"
        file_path - caminho do ficheiro enviado (None se não houver)
        id        - identificador único
        timestamp - quando foi enviada
    """
    username: str
    text: str
    room_id: str = "geral"
    msg_type: str = "chat"
    file_path: str = None        # novo campo para ficheiros
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)