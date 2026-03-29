# models/message.py

from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class Message:
    """
    Representa uma mensagem enviada no chat.

    Atributos:
        username  - quem enviou a mensagem
        text      - o conteúdo da mensagem
        room_id   - em que sala foi enviada (por defeito "geral")
        msg_type  - "chat" para mensagens normais, "login" para avisos de entrada
        id        - identificador único gerado automaticamente
        timestamp - quando foi enviada, gerado automaticamente
    """

    username: str
    text: str
    room_id: str = "geral"
    msg_type: str = "chat"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)