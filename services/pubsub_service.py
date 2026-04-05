# services/pubsub_service.py

# Dicionário global de utilizadores online {username: avatar_color}
online_users: dict = {}

# Dicionário global de estados {username: status}
user_statuses: dict = {}


def get_private_topic(user1: str, user2: str) -> str:
    names = sorted([user1, user2])
    return f"priv_{names[0]}_{names[1]}"


def user_join(username: str, avatar_color: str, page, on_users_change):
    online_users[username] = avatar_color
    user_statuses[username] = "disponivel"
    page.pubsub.send_all_on_topic("users_online", online_users.copy())


def user_leave(username: str, page):
    if username in online_users:
        del online_users[username]
    if username in user_statuses:
        del user_statuses[username]
    page.pubsub.send_all_on_topic("users_online", online_users.copy())


def update_status(username: str, status: str, page):
    user_statuses[username] = status
    page.pubsub.send_all_on_topic("status_update", user_statuses.copy())


def subscribe(page, handler):
    page.pubsub.subscribe(handler)


def subscribe_to_room(page, room_id, handler):
    page.pubsub.subscribe_topic(room_id, handler)


def subscribe_to_private(page, topic, handler):
    page.pubsub.subscribe_topic(topic, handler)


def subscribe_to_users(page, handler):
    page.pubsub.subscribe_topic("users_online", handler)


def subscribe_to_status(page, handler):
    page.pubsub.subscribe_topic("status_update", handler)


def unsubscribe_from_room(page, room_id):
    page.pubsub.unsubscribe_topic(room_id)


def unsubscribe(page):
    page.pubsub.unsubscribe_all()


def broadcast(page, message):
    page.pubsub.send_all(message)


def broadcast_to_room(page, room_id, message):
    page.pubsub.send_all_on_topic(room_id, message)


def broadcast_to_private(page, topic, message):
    page.pubsub.send_all_on_topic(topic, message)