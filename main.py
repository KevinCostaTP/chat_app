# main.py

import flet as ft
import random
from models.user import User
from models.room import Room
from components.chat_view import ChatView
from components.sidebar import Sidebar
from services import db_service


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

        # Carrega a sala Geral como sala inicial
        rooms = db_service.get_all_rooms()
        current_room = rooms[0]  # primeira sala = Geral

        # Referência mutável à sala atual
        # Usamos uma lista com um elemento para poder modificar dentro das funções
        room_ref = [current_room]

        # Container do chat que vai ser substituído ao mudar de sala
        chat_container = ft.Container(expand=True)

        def build_chat(room):
            """Constrói a vista do chat para a sala indicada."""
            # Cancela a subscrição da sala anterior
            if room_ref[0].id != room.id:
                pubsub_service_unsubscribe(room_ref[0].id)

            room_ref[0] = room
            chat_container.content = ChatView(page, user, room)
            page.update()

        def pubsub_service_unsubscribe(room_id):
            page.pubsub.unsubscribe_topic(room_id)

        def on_room_change(room):
            """Chamada pelo Sidebar quando o utilizador clica numa sala."""
            build_chat(room)
            # Reconstrói o layout para atualizar o sidebar
            rebuild_layout(user, room)

        def rebuild_layout(user, room):
            """Reconstrói o layout completo com o sidebar atualizado."""
            page.clean()
            page.vertical_alignment = ft.MainAxisAlignment.START

            sidebar = Sidebar(page, user, room, on_room_change)
            chat_view = ChatView(page, user, room)

            page.add(
                ft.Row(
                    controls=[sidebar, ft.Container(content=chat_view, expand=True)],
                    expand=True,
                    spacing=0,
                )
            )

        # Constrói o layout inicial
        rebuild_layout(user, current_room)

    username_field = ft.TextField(
        label="O teu nome",
        hint_text="Ex: João, Maria...",
        autofocus=True,
        width=300,
        border_radius=12,
        on_submit=show_chat,
    )

    page.add(
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


# Inicializa a base de dados antes de arrancar
db_service.init_db()

ft.run(main, view=ft.AppView.WEB_BROWSER, port=8080)