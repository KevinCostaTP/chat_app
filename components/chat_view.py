# components/chat_view.py

import flet as ft
from models.message import Message
from components.message_bubble import MessageBubble
from services import pubsub_service


def ChatView(page: ft.Page, current_user, current_room):
    """
    A vista principal do chat — adaptada para suportar salas.

    Parâmetros:
        page         - a página Flet
        current_user - objeto User do utilizador atual
        current_room - objeto Room da sala atual
    """

    messages_list = ft.ListView(
        expand=1,
        spacing=4,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text=f"Mensagem em #{current_room.name}...",
        expand=True,
        shift_enter=True,
        min_lines=1,
        max_lines=4,
        border_radius=20,
        filled=True,
        on_submit=lambda e: send_message(e),
    )

    def on_message_received(topic, message):
        """
        Chamada pelo PubSub quando chega mensagem NESTA sala.
        O 'topic' é o id da sala — não usamos mas o Flet passa-o sempre.
        """
        messages_list.controls.append(
            MessageBubble(message, current_user)
        )
        page.update()

    def send_message(e):
        if not new_message.value.strip():
            return

        msg = Message(
            username=current_user.username,
            text=new_message.value.strip(),
            room_id=current_room.id,
        )

        # Envia só para esta sala
        pubsub_service.broadcast_to_room(page, current_room.id, msg)

        new_message.value = ""
        page.update()

    # Subscreve ao tópico desta sala
    pubsub_service.subscribe_to_room(page, current_room.id, on_message_received)

    # Avisa a sala que este utilizador entrou
    pubsub_service.broadcast_to_room(page, current_room.id, Message(
        username=current_user.username,
        text=f"{current_user.username} entrou em #{current_room.name} 👋",
        room_id=current_room.id,
        msg_type="login",
    ))

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        icon_color=ft.Colors.BLUE_600,
        tooltip="Enviar mensagem",
        on_click=send_message,
    )

    header = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.TAG, color=ft.Colors.BLUE_600),
                ft.Text(
                    current_room.name,
                    size=16,
                    weight=ft.FontWeight.BOLD,
                ),
            ],
        ),
        padding=ft.padding.symmetric(vertical=12, horizontal=16),
        bgcolor=ft.Colors.SURFACE,
    )

    input_bar = ft.Container(
        content=ft.Row(
            controls=[new_message, send_button],
            spacing=8,
        ),
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
    )

    return ft.Column(
        controls=[
            header,
            ft.Container(content=messages_list, expand=True),
            ft.Divider(height=1),
            input_bar,
        ],
        expand=True,
        spacing=0,
    )