# components/chat_view.py

import flet as ft
from models.message import Message
from components.message_bubble import MessageBubble
from services import pubsub_service, file_service


def ChatView(page: ft.Page, current_user, current_room=None, private_user=None, file_picker=None):

    is_private = private_user is not None

    if is_private:
        topic = pubsub_service.get_private_topic(
            current_user.username,
            private_user["username"]
        )
        chat_name = private_user["username"]
    else:
        topic = current_room.id
        chat_name = current_room.name

    messages_list = ft.ListView(
        expand=1,
        spacing=4,
        auto_scroll=True,
    )

    new_message = ft.TextField(
        hint_text=(
            f"Mensagem privada para {chat_name}..."
            if is_private
            else f"Mensagem em #{chat_name}..."
        ),
        expand=True,
        shift_enter=True,
        min_lines=1,
        max_lines=4,
        border_radius=20,
        filled=True,
        on_submit=lambda e: send_message(e),
    )

    def on_message_received(topic, message):
        messages_list.controls.append(
            MessageBubble(message, current_user)
        )
        page.update()

    def send_message(e, file_path=None):
        text = new_message.value.strip()

        if not text and not file_path:
            return

        msg = Message(
            username=current_user.username,
            text=text,
            room_id=topic,
            file_path=file_path,
        )

        if is_private:
            pubsub_service.broadcast_to_private(page, topic, msg)
        else:
            pubsub_service.broadcast_to_room(page, topic, msg)

        new_message.value = ""
        page.update()

    def show_file_dialog(e):
        """
        Mostra um dialog onde o utilizador cola o caminho do ficheiro.
        Funciona sempre em modo web sem problemas.
        """
        path_field = ft.TextField(
            label="Caminho do ficheiro",
            hint_text="Ex: C:\\Users\\...\\imagem.jpg",
            expand=True,
            autofocus=True,
            border_radius=8,
        )

        def send_file(e):
            path = path_field.value.strip()
            if not path:
                path_field.error_text = "Insere o caminho do ficheiro"
                page.update()
                return

            saved_path = file_service.save_file(path)
            if saved_path:
                dialog.open = False
                page.update()
                send_message(None, file_path=saved_path)
            else:
                path_field.error_text = "Ficheiro não encontrado. Verifica o caminho."
                page.update()

        def close_dialog(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enviar ficheiro"),
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Cola o caminho completo do ficheiro abaixo:",
                        size=13,
                        color=ft.Colors.GREY_600,
                    ),
                    path_field,
                ],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.TextButton("Enviar", on_click=send_file),
            ],
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        icon_color=ft.Colors.BLUE_600,
        tooltip="Enviar mensagem",
        on_click=send_message,
    )

    attach_button = ft.IconButton(
        icon=ft.Icons.ATTACH_FILE,
        icon_color=ft.Colors.GREY_600,
        tooltip="Enviar ficheiro",
        on_click=show_file_dialog,
    )

    if is_private:
        header_content = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(
                        private_user["username"][0].upper(),
                        color=ft.Colors.WHITE,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    bgcolor=private_user["avatar_color"],
                    radius=16,
                ),
                ft.Column(
                    controls=[
                        ft.Text(
                            private_user["username"],
                            size=15,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Mensagem direta",
                            size=11,
                            color=ft.Colors.GREY_500,
                        ),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
        )
    else:
        header_content = ft.Row(
            controls=[
                ft.Icon(ft.Icons.TAG, color=ft.Colors.BLUE_600),
                ft.Text(chat_name, size=16, weight=ft.FontWeight.BOLD),
            ],
        )

    header = ft.Container(
        content=header_content,
        padding=ft.padding.symmetric(vertical=12, horizontal=16),
        bgcolor=ft.Colors.SURFACE,
    )

    input_bar = ft.Container(
        content=ft.Row(
            controls=[attach_button, new_message, send_button],
            spacing=4,
        ),
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
    )

    if is_private:
        pubsub_service.subscribe_to_private(page, topic, on_message_received)
    else:
        pubsub_service.subscribe_to_room(page, topic, on_message_received)
        pubsub_service.broadcast_to_room(page, topic, Message(
            username=current_user.username,
            text=f"{current_user.username} entrou em #{chat_name} 👋",
            room_id=topic,
            msg_type="login",
        ))

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