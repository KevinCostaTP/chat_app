# models/user.py

class User:
    def __init__(self, username: str, avatar_color: str, status: str = "disponivel"):
        self.username = username
        self.avatar_color = avatar_color
        self.status = status  # disponivel, ocupado, ausente