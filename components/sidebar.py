# components/sidebar.py

import flet as ft
from models.room import Room
from services import db_service


def Sidebar(page, current_user, current_room, on_room_change):
    """
    Painel lateral com a lista de salas e botão para criar salas novas.

    Parâmetros:
        page           - a página Flet
        current_user   - objeto User do utilizador atual
        current_room   - objeto Room da sala atual
        on_room_change - função chamada quando o utilizador muda de sala
    """

    # Lista de salas que vai ser atualizada dinamicamente
    rooms_list = ft.Column(spacing=4)

    def build_rooms_list():
        """
        Constrói a lista de salas a partir do DuckDB.
        Chamada sempre que uma sala é criada ou alterada.
        """
        rooms_list.controls.clear()
        rooms = db_service.get_all_rooms()

        for room in rooms:
            # Verifica se é a sala atual para destacar
            is_current = room.id == current_room.id

            rooms_list.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.TAG,
                                size=16,
                                color=ft.Colors.BLUE_600 if is_current else ft.Colors.GREY_500,
                            ),
                            ft.Text(
                                room.name,
                                size=14,
                                weight=ft.FontWeight.BOLD if is_current else ft.FontWeight.NORMAL,
                                color=ft.Colors.BLUE_600 if is_current else ft.Colors.BLACK87,
                            ),
                        ],
                        spacing=8,
                    ),
                    padding=ft.padding.symmetric(vertical=8, horizontal=12),
                    border_radius=8,
                    bgcolor=ft.Colors.BLUE_50 if is_current else None,
                    on_click=lambda e, r=room: on_room_change(r),
                    ink=True,  # efeito de ripple ao clicar
                )
            )

    def show_create_room_dialog(e):
        """
        Mostra um dialog para criar uma sala nova.
        """
        room_name_field = ft.TextField(
            label="Nome da sala",
            hint_text="Ex: Jogos, Música...",
            autofocus=True,
            border_radius=8,
        )

        def create_room(e):
            name = room_name_field.value.strip()

            # Validações
            if not name:
                room_name_field.error_text = "Escreve um nome para a sala"
                page.update()
                return

            if db_service.room_exists(name):
                room_name_field.error_text = "Já existe uma sala com este nome"
                page.update()
                return

            # Cria e guarda a sala
            new_room = Room(name=name, created_by=current_user.username)
            db_service.save_room(new_room)

            # Fecha o dialog
            dialog.open = False

            # Atualiza a lista de salas e muda para a nova sala
            build_rooms_list()
            on_room_change(new_room)
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Criar sala nova"),
            content=ft.Column(
                controls=[room_name_field],
                tight=True,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: close_dialog(e)),
                ft.TextButton("Criar", on_click=create_room),
            ],
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # Constrói a lista inicial
    build_rooms_list()

    # Sidebar completo
    return ft.Container(
        content=ft.Column(
            controls=[
                # Cabeçalho do sidebar
                ft.Container(
                    content=ft.Text(
                        "Salas",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                    ),
                    padding=ft.padding.symmetric(vertical=16, horizontal=12),
                ),

                ft.Divider(height=1),

                # Lista de salas
                ft.Container(
                    content=rooms_list,
                    expand=True,
                    padding=ft.padding.symmetric(vertical=8, horizontal=4),
                ),

                ft.Divider(height=1),

                # Botão para criar sala nova
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.ADD, size=18, color=ft.Colors.BLUE_600),
                                ft.Text("Nova sala", color=ft.Colors.BLUE_600),
                            ],
                            spacing=6,
                        ),
                        on_click=show_create_room_dialog,
                    ),
                    padding=ft.padding.symmetric(vertical=8, horizontal=8),
                ),

                # Info do utilizador atual em baixo
                ft.Divider(height=1),
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