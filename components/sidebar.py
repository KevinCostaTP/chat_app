# components/sidebar.py

import flet as ft
from models.room import Room
from services import db_service, pubsub_service

STATUS_COLORS = {
    "disponivel": ft.Colors.GREEN_400,
    "ocupado": ft.Colors.ORANGE_400,
    "ausente": ft.Colors.RED_400,
}

STATUS_LABELS = {
    "disponivel": "Disponível",
    "ocupado": "Ocupado",
    "ausente": "Ausente",
}

AVATAR_COLORS = [
    ft.Colors.BLUE_400,
    ft.Colors.GREEN_400,
    ft.Colors.ORANGE_400,
    ft.Colors.PURPLE_400,
    ft.Colors.RED_400,
    ft.Colors.TEAL_400,
    ft.Colors.PINK_400,
]


def Sidebar(page, current_user, current_room, on_room_change, on_private_chat):

    rooms_list = ft.Column(spacing=2)
    users_list = ft.Column(spacing=2)

    def build_rooms_list():
        rooms_list.controls.clear()
        rooms = db_service.get_all_rooms()

        for room in rooms:
            is_current = current_room is not None and room.id == current_room.id

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
        users_list.controls.clear()
        statuses = pubsub_service.user_statuses

        for username, avatar_color in users.items():
            if username == current_user.username:
                continue

            status = statuses.get(username, "disponivel")
            status_color = STATUS_COLORS.get(status, ft.Colors.GREEN_400)

            users_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
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
                                        bgcolor=status_color,
                                        border_radius=4,
                                        right=0,
                                        bottom=0,
                                    ),
                                ],
                                width=24,
                                height=24,
                            ),
                            ft.Text(username, size=13, color=ft.Colors.BLACK87),
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
        build_users_list(users)

    def on_status_update(topic, statuses):
        build_users_list(pubsub_service.online_users)

    pubsub_service.subscribe_to_users(page, on_users_update)
    pubsub_service.subscribe_to_status(page, on_status_update)

    def show_create_room_dialog(e):
        room_name_field = ft.TextField(
            label="Nome da sala",
            hint_text="Ex: Jogos, Música...",
            autofocus=True,
            border_radius=8,
        )

        def create_room(e):
            name = room_name_field.value.strip()
            if not name:
                room_name_field.error_text = "Escreve um nome"
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

        def close(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Criar sala nova"),
            content=ft.Column(controls=[room_name_field], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close),
                ft.TextButton("Criar", on_click=create_room),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def show_profile_dialog(e):
        """Dialog para editar o perfil do utilizador."""
        selected_status = [current_user.status]
        selected_color = [current_user.avatar_color]

        status_dropdown = ft.Dropdown(
            label="Estado",
            value=current_user.status,
            options=[
                ft.dropdown.Option("disponivel", "🟢 Disponível"),
                ft.dropdown.Option("ocupado", "🟡 Ocupado"),
                ft.dropdown.Option("ausente", "🔴 Ausente"),
            ],
            border_radius=8,
            on_change=lambda e: selected_status.__setitem__(0, e.control.value),
        )

        def save_profile(e):
            current_user.status = selected_status[0]
            pubsub_service.user_statuses[current_user.username] = selected_status[0]
            pubsub_service.update_status(current_user.username, selected_status[0], page)
            dialog.open = False
            page.update()

        def close(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("O meu perfil"),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(
                                    current_user.username[0].upper(),
                                    color=ft.Colors.WHITE,
                                    size=20,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=current_user.avatar_color,
                                radius=24,
                            ),
                            ft.Text(
                                current_user.username,
                                size=16,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=12,
                    ),
                    ft.Divider(),
                    status_dropdown,
                ],
                tight=True,
                spacing=12,
                width=280,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close),
                ft.TextButton("Guardar", on_click=save_profile),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    build_rooms_list()
    build_users_list(pubsub_service.online_users)

    # Indicador de status do utilizador atual
    my_status = current_user.status
    my_status_color = STATUS_COLORS.get(my_status, ft.Colors.GREEN_400)

    return ft.Container(
        content=ft.Column(
            controls=[
                # Cabeçalho
                ft.Container(
                    content=ft.Text("Chat App", size=16, weight=ft.FontWeight.BOLD),
                    padding=ft.padding.symmetric(vertical=16, horizontal=12),
                ),

                ft.Divider(height=1),

                # Salas
                ft.Container(
                    content=ft.Text("SALAS", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500),
                    padding=ft.padding.only(left=12, top=12, bottom=4),
                ),
                ft.Container(content=rooms_list, padding=ft.padding.symmetric(horizontal=4)),
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

                # Mensagens diretas
                ft.Container(
                    content=ft.Text("MENSAGENS DIRETAS", size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_500),
                    padding=ft.padding.only(left=12, top=12, bottom=4),
                ),
                ft.Container(
                    content=users_list,
                    expand=True,
                    padding=ft.padding.symmetric(horizontal=4),
                ),

                ft.Divider(height=1),

                # Perfil do utilizador atual (clicável)
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Stack(
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
                                    ft.Container(
                                        width=8,
                                        height=8,
                                        bgcolor=my_status_color,
                                        border_radius=4,
                                        right=0,
                                        bottom=0,
                                    ),
                                ],
                                width=28,
                                height=28,
                            ),
                            ft.Column(
                                controls=[
                                    ft.Text(current_user.username, size=13, weight=ft.FontWeight.W_500),
                                    ft.Text(
                                        STATUS_LABELS.get(my_status, "Disponível"),
                                        size=11,
                                        color=ft.Colors.GREY_500,
                                    ),
                                ],
                                spacing=0,
                            ),
                            ft.Container(expand=True),
                            ft.IconButton(
                                icon=ft.Icons.SETTINGS,
                                icon_size=16,
                                icon_color=ft.Colors.GREY_500,
                                tooltip="Editar perfil",
                                on_click=show_profile_dialog,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    ink=True,
                    on_click=show_profile_dialog,
                ),
            ],
            expand=True,
            spacing=0,
        ),
        width=220,
        bgcolor=ft.Colors.GREY_100,
        border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_300)),
    )