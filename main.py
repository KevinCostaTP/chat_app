# main.py

import flet as ft
import random
from models.user import User
from components.chat_view import ChatView


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

        page.clean()
        page.vertical_alignment = ft.MainAxisAlignment.START
        page.add(ChatView(page, user))

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
                ft.Icon(
                    ft.Icons.CHAT,
                    size=72,
                    color=ft.Colors.BLUE_600,
                ),
                ft.Text(
                    "Chat App",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
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


ft.run(main, view=ft.AppView.WEB_BROWSER, port=8080)