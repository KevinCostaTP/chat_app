# components/sidebar.py

import flet as ft
from models.room import Room
from services import db_service, pubsub_service


def Sidebar(page, current_user, current_room, on_room_change, on_private_chat):
    """
    Painel lateral com salas e utilizadores online.

    Parâmetros:
        page           - a página Flet
        current_user   - objeto User do utilizador atual
        current_room   - objeto Room da sala atual (None se for conversa privada)
        on_room_change - função chamada quando muda de sala
        on_private_chat - função chamada quando inicia conversa privada
    """

    rooms_list = ft.Column(spacing=2)
    users_list = ft.Column(spacing=2)

    def build_rooms_list():
        """Constrói a lista de salas."""
        rooms_list.controls.clear()
        rooms = db_service.get_all_rooms()

        for room in rooms:
            is_current = (
                current_room is not None and
                room.id == current_room.id
            )

            rooms_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.TAG,
                                size=14,
                                color=ft.Colors.BLUE_600 if is_current else ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                room.name,
                                size=13,
                                weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                                color=ft.Colors.BLUE_600 if is_current else ft.Colors.BLACK87,
                            ),
                        ],
                        spacing=6,
                    ),
                    padding=ft.padding.symmetric(vertical=6, horizontal=10),
                    border_radius=6,
                    bgcolor=ft.Colors.BLUE_50 if is_current else None,
                    on_click=lambda e, r=room: on_room_change(r),
                    ink=True,
                )
            )

    def build_users_list(users: dict):
        """
        Constrói a lista de utilizadores online.

        Parâmetros:
            users - dicionário {username: avatar_color}
        """
        users_list.controls.clear()

        for username, avatar_color in users.items():
            # Não mostra o próprio utilizador na lista
            if username == current_user.username:
                continue

            users_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            # Indicador verde de online
                            ft.Stack(
                                controls=[
                                    ft.CircleAvatar(
                                        content=ft.Text(
                                            username[0].upper(),
                                            color=ft.Colors.WHITE,
                                            size=11,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        bgcolor=avatar_color,
                                        radius=12,
                                    ),
                                    ft.Container(
                                        width=8,
                                        height=8,
                                        bgcolor=ft.Colors.GREEN_400,
                                        border_radius=4,
                                        right=0,
                                        bottom=0,
                                    ),
                                ],
                                width=24,
                                height=24,
                            ),
                            ft.Text(
                                username,
                                size=13,
                                color=ft.Colors.BLACK87,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(vertical=6, horizontal=10),
                    border_radius=6,
                    on_click=lambda e, u=username, c=avatar_color: on_private_chat(u, c),
                    ink=True,
                )
            )

        if not users_list.controls:
            users_list.controls.append(
                ft.Text(
                    "Nenhum utilizador online",
                    size=12,
                    color=ft.Colors.GREY_500,
                    italic=True,
                )
            )

        page.update()

    def on_users_update(topic, users):
        """
        Chamada pelo PubSub quando a lista de utilizadores muda.
        Reconstrói a lista visualmente.
        """
        build_users_list(users)

    # Subscreve para receber atualizações de utilizadores online
    pubsub_service.subscribe_to_users(page, on_users_update)

    def show_create_room_dialog(e):
        """Mostra popup para criar sala nova."""
        room_name_field = ft.TextField(
            label="Nome da sala",
            hint_text="Ex: Jogos, Música...",
            autofocus=True,
            border_radius=8,
        )

        def create_room(e):
            name = room_name_field.value.strip()

            if not name:
                room_name_field.error_text = "Escreve um nome para a sala"
                page.update()
                return

            if db_service.room_exists(name):
                room_name_field.error_text = "Já existe uma sala com este nome"
                page.update()
                return

            new_room = Room(name=name, created_by=current_user.username)
            db_service.save_room(new_room)

            dialog.open = False
            build_rooms_list()
            on_room_change(new_room)
            page.update()

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Criar sala nova"),
            content=ft.Column(controls=[room_name_field], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.TextButton("Criar", on_click=create_room),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Constrói as listas iniciais
    build_rooms_list()
    build_users_list(pubsub_service.online_users)

    return ft.Container(
        content=ft.Column(
            controls=[
                # Cabeçalho
                ft.Container(
                    content=ft.Text("Chat App", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(vertical=16, horizontal=12),
                ),

                ft.Divider(height=1),

                # Secção de salas
                ft.Container(
                    content=ft.Text(
                        "SALAS",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_500,
                    ),
                    padding=ft.padding.only(left=12, top=12, bottom=4),
                ),
                ft.Container(
                    content=rooms_list,
                    padding=ft.padding.symmetric(horizontal=4),
                ),

                # Botão nova sala
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADD, size=16, color=ft.Colors.BLUE_600),
                                ft.Text("Nova sala", size=12, color=ft.Colors.BLUE_600),
                            ],
                            spacing=4,
                        ),
                        on_click=show_create_room_dialog,
                    ),
                    padding=ft.padding.only(left=4, bottom=8),
                ),

                ft.Divider(height=1),

                # Secção de mensagens diretas
                ft.Container(
                    content=ft.Text(
                        "MENSAGENS DIRETAS",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.GREY_500,
                    ),
                    padding=ft.padding.only(left=12, top=12, bottom=4),
                ),
                ft.Container(
                    content=users_list,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=4),
                ),

                ft.Divider(height=1),

                # Utilizador atual no rodapé
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(
                                    current_user.username[0].upper(),
                                    color=ft.Colors.WHITE,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=current_user.avatar_color,
                                radius=14,
                            ),
                            ft.Text(
                                current_user.username,
                                size=13,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(vertical=12, horizontal=12),
                ),
            ],
            expand=True,
            spacing=0,
        ),
        width=220,
        bgcolor=ft.Colors.GREY_100,
        border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_300)),
    )