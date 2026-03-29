# components/chat_view.py

import flet as ft
from models.message import Message
from components.message_bubble import MessageBubble
from services import pubsub_service


def ChatView(page: ft.Page, current_user):

    messages_list = ft.ListView(
        expand=1,
        spacing=4,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text="Escreve uma mensagem...",
        expand=True,
        shift_enter=True,
        min_lines=1,
        max_lines=4,
        border_radius=20,
        filled=True,
        on_submit=lambda e: send_message(e),
    )

    def on_message_received(message):
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
        )

        pubsub_service.broadcast(page, msg)
        new_message.value = ""
        page.update()

    pubsub_service.subscribe(page, on_message_received)

    pubsub_service.broadcast(page, Message(
        username=current_user.username,
        text=f"{current_user.username} entrou no chat 👋",
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
                ft.Icon(ft.Icons.CHAT, color=ft.Colors.BLUE_600),
                ft.Text("Sala Geral", size=16, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                ft.CircleAvatar(
                    content=ft.Text(
                        current_user.username[0].upper(),
                        color=ft.Colors.WHITE,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=current_user.avatar_color,
                    radius=16,
                ),
                ft.Text(
                    current_user.username,
                    size=13,
                    color=ft.Colors.GREY_600,
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