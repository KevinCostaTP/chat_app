# services/pubsub_service.py

# Dicionário global que guarda os utilizadores online
# Chave: username, Valor: avatar_color
# É global porque precisa de ser partilhado entre todas as sessões
online_users: dict = {}


def get_private_topic(user1: str, user2: str) -> str:
    """
    Gera um tópico único para uma conversa privada entre dois utilizadores.
    Ordena os nomes alfabeticamente para garantir que "priv_Ana_João"
    e "priv_João_Ana" geram sempre o mesmo tópico.

    Exemplo: get_private_topic("João", "Ana") → "priv_Ana_João"
    """
    names = sorted([user1, user2])
    return f"priv_{names[0]}_{names[1]}"


def user_join(username: str, avatar_color: str, page, on_users_change):
    """
    Regista um utilizador como online e notifica todos.

    Parâmetros:
        username       - o nome do utilizador
        avatar_color   - a cor do avatar
        page           - a página Flet
        on_users_change - função chamada quando a lista muda
    """
    online_users[username] = avatar_color
    # Notifica todos os utilizadores que a lista mudou
    page.pubsub.send_all_on_topic("users_online", online_users.copy())


def user_leave(username: str, page):
    """
    Remove um utilizador da lista de online e notifica todos.
    Chamada quando o utilizador fecha a app.
    """
    if username in online_users:
        del online_users[username]
    page.pubsub.send_all_on_topic("users_online", online_users.copy())


def subscribe_to_users(page, handler):
    """
    Subscreve para receber atualizações da lista de utilizadores online.
    """
    page.pubsub.subscribe_topic("users_online", handler)


def subscribe(page, handler):
    """Subscreve ao canal global."""
    page.pubsub.subscribe(handler)


def subscribe_to_room(page, room_id, handler):
    """Subscreve ao tópico de uma sala específica."""
    page.pubsub.subscribe_topic(room_id, handler)


def subscribe_to_private(page, topic, handler):
    """
    Subscreve ao tópico de uma conversa privada.

    Parâmetros:
        topic - gerado por get_private_topic()
    """
    page.pubsub.subscribe_topic(topic, handler)


def unsubscribe_from_room(page, room_id):
    """Cancela a subscrição de uma sala."""
    page.pubsub.unsubscribe_topic(room_id)


def unsubscribe(page):
    """Cancela todas as subscrições."""
    page.pubsub.unsubscribe_all()


def broadcast(page, message):
    """Envia para todos os utilizadores."""
    page.pubsub.send_all(message)


def broadcast_to_room(page, room_id, message):
    """Envia apenas para os utilizadores de uma sala."""
    page.pubsub.send_all_on_topic(room_id, message)


def broadcast_to_private(page, topic, message):
    """
    Envia uma mensagem privada.
    Só os dois utilizadores subscritos ao tópico recebem.
    """
    page.pubsub.send_all_on_topic(topic, message)