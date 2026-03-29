# models/user.py

class User:
    """
    Representa um utilizador ligado à aplicação.

    Atributos:
        username     - o nome escolhido pelo utilizador
        avatar_color - a cor do avatar (círculo colorido com a inicial do nome)
    """

    def __init__(self, username: str, avatar_color: str):
        self.username = username
        self.avatar_color = avatar_color