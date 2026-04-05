# main.py

import flet as ft
import random
from models.user import User
from components.chat_view import ChatView
from components.sidebar import Sidebar
from services import db_service, pubsub_service, file_service


AVATAR_COLORS = [
    ft.Colors.BLUE_400,
    ft.Colors.GREEN_400,
    ft.Colors.ORANGE_400,
    ft.Colors.PURPLE_400,
    ft.Colors.RED_400,
    ft.Colors.TEAL_400,
    ft.Colors.PINK_400,
]


def main(page: ft.Page):
    page.title = "Chat App"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0

    def show_chat(e):
        if not username_field.value.strip():
            username_field.error_text = "Escolhe um nome para continuar"
            page.update()
            return

        user = User(
            username=username_field.value.strip(),
            avatar_color=random.choice(AVATAR_COLORS),
        )

        rooms = db_service.get_all_rooms()
        current_room_ref = [rooms[0]]
        current_private_ref = [None]

        def rebuild_layout(room=None, private_user=None):
            # Cancela subscrições anteriores
            if current_room_ref[0] is not None:
                pubsub_service.unsubscribe_from_room(page, current_room_ref[0].id)
            if current_private_ref[0] is not None:
                old_topic = pubsub_service.get_private_topic(
                    user.username,
                    current_private_ref[0]["username"]
                )
                pubsub_service.unsubscribe_from_room(page, old_topic)

            current_room_ref[0] = room
            current_private_ref[0] = private_user

            page.controls.clear()
            page.vertical_alignment = ft.MainAxisAlignment.START

            if private_user:
                chat = ChatView(page, user, private_user=private_user)
            else:
                chat = ChatView(page, user, current_room=room)

            sidebar = Sidebar(
                page=page,
                current_user=user,
                current_room=room,
                on_room_change=on_room_change,
                on_private_chat=on_private_chat,
            )

            page.controls.append(
                ft.Row(
                    controls=[
                        sidebar,
                        ft.Container(content=chat, expand=True),
                    ],
                    expand=True,
                    spacing=0,
                )
            )
            page.update()

        def on_room_change(room):
            rebuild_layout(room=room)

        def on_private_chat(username, avatar_color):
            rebuild_layout(private_user={
                "username": username,
                "avatar_color": avatar_color,
            })

        pubsub_service.user_join(
            user.username,
            user.avatar_color,
            page,
            lambda users: None,
        )

        def on_disconnect(e):
            pubsub_service.user_leave(user.username, page)

        page.on_close = on_disconnect
        rebuild_layout(room=rooms[0])

    username_field = ft.TextField(
        label="O teu nome",
        hint_text="Ex: João, Maria...",
        autofocus=True,
        width=300,
        border_radius=12,
        on_submit=show_chat,
    )

    page.controls.append(
        ft.Column(
            controls=[
                ft.Icon(ft.Icons.CHAT, size=72, color=ft.Colors.BLUE_600),
                ft.Text("Chat App", size=32, weight=ft.FontWeight.BOLD),
                ft.Text(
                    "Entra com o teu nome para começar",
                    size=14,
                    color=ft.Colors.GREY_600,
                ),
                ft.Divider(height=24, color=ft.Colors.TRANSPARENT),
                username_field,
                ft.Button(
                    content=ft.Text("Entrar no chat", color=ft.Colors.WHITE),
                    width=300,
                    height=48,
                    on_click=show_chat,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.BLUE_600,
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
        )
    )
    page.update()


db_service.init_db()
file_service.ensure_uploads_dir()
ft.run(main, view=ft.AppView.WEB_BROWSER, port=8080)