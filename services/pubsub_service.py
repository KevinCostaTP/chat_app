# services/pubsub_service.py


def subscribe(page, handler):
    """
    Subscreve este utilizador para receber mensagens globais.
    Usado para avisos de sistema (ex: nova sala criada).
    """
    page.pubsub.subscribe(handler)


def subscribe_to_room(page, room_id, handler):
    """
    Subscreve este utilizador ao tópico de uma sala específica.
    Só recebe mensagens dessa sala.

    Parâmetros:
        room_id - o id da sala (ex: "sala-geral")
        handler - função chamada quando chega mensagem nesta sala
    """
    page.pubsub.subscribe_topic(room_id, handler)


def unsubscribe_from_room(page, room_id):
    """
    Cancela a subscrição de uma sala.
    Chamada quando o utilizador muda de sala.
    """
    page.pubsub.unsubscribe_topic(room_id)


def unsubscribe(page):
    """
    Cancela todas as subscrições quando o utilizador fecha a app.
    """
    page.pubsub.unsubscribe_all()


def broadcast(page, message):
    """
    Envia uma mensagem para TODOS os utilizadores ligados.
    Usado para avisos globais (ex: nova sala criada).
    """
    page.pubsub.send_all(message)


def broadcast_to_room(page, room_id, message):
    """
    Envia uma mensagem APENAS para os utilizadores da sala.

    Parâmetros:
        room_id - o id da sala de destino
        message - objeto Message a enviar
    """
    page.pubsub.send_all_on_topic(room_id, message)