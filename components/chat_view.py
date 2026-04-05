# components/chat_view.py

import flet as ft
from models.message import Message
from components.message_bubble import MessageBubble, REACTION_EMOJIS
from services import pubsub_service, file_service


DEFAULT_STICKERS = [
    "😂", "❤️", "🔥", "👏", "🎉", "😎",
    "🤔", "👍", "😍", "🙏", "💪", "🥳",
    "😭", "🤣", "✨", "😅", "🫶", "💯",
]


def ChatView(page: ft.Page, current_user, current_room=None, private_user=None):

    is_private = private_user is not None

    if is_private:
        topic = pubsub_service.get_private_topic(
            current_user.username, private_user["username"]
        )
        chat_name = private_user["username"]
    else:
        topic = current_room.id
        chat_name = current_room.name

    messages_list = ft.ListView(expand=1, spacing=4, auto_scroll=True)

    # Dicionários para rastrear mensagens e os seus containers
    messages_store = {}   # {message_id: Message}
    bubble_map = {}       # {message_id: ft.Container}

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

    # ── Funções de atualização de bubbles ──────────────

    def rebuild_bubble(message_id):
        """Substitui um bubble existente por um atualizado."""
        if message_id not in messages_store:
            return

        msg = messages_store[message_id]
        new_bubble = MessageBubble(
            msg, current_user, page,
            on_edit=handle_edit,
            on_delete=handle_delete,
            on_react=handle_react,
        )

        for i, ctrl in enumerate(messages_list.controls):
            if hasattr(ctrl, "data") and ctrl.data == message_id:
                messages_list.controls[i] = new_bubble
                bubble_map[message_id] = new_bubble
                break

        page.update()

    # ── Handlers de editar, eliminar, reagir ──────────

    def handle_edit(message):
        edit_field = ft.TextField(
            value=message.text,
            multiline=True,
            autofocus=True,
            border_radius=8,
            expand=True,
        )

        def save_edit(e):
            new_text = edit_field.value.strip()
            if not new_text:
                return

            messages_store[message.id].text = new_text
            messages_store[message.id].is_edited = True

            edit_msg = Message(
                username=current_user.username,
                text=new_text,
                room_id=topic,
                msg_type="edit",
                id=message.id,
            )

            if is_private:
                pubsub_service.broadcast_to_private(page, topic, edit_msg)
            else:
                pubsub_service.broadcast_to_room(page, topic, edit_msg)

            dialog.open = False
            rebuild_bubble(message.id)

        def close(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Editar mensagem"),
            content=ft.Column(controls=[edit_field], tight=True),
            actions=[
                ft.TextButton("Cancelar", on_click=close),
                ft.TextButton("Guardar", on_click=save_edit),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def handle_delete(message):
        def confirm(e):
            messages_store[message.id].is_deleted = True

            del_msg = Message(
                username=current_user.username,
                text="",
                room_id=topic,
                msg_type="delete",
                id=message.id,
            )

            if is_private:
                pubsub_service.broadcast_to_private(page, topic, del_msg)
            else:
                pubsub_service.broadcast_to_room(page, topic, del_msg)

            dialog.open = False
            rebuild_bubble(message.id)

        def close(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Eliminar mensagem"),
            content=ft.Text("Tens a certeza que queres eliminar esta mensagem?"),
            actions=[
                ft.TextButton("Cancelar", on_click=close),
                ft.TextButton(
                    "Eliminar",
                    on_click=confirm,
                    style=ft.ButtonStyle(color=ft.Colors.RED_400),
                ),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def handle_react(message, emoji):
        msg = messages_store.get(message.id)
        if not msg:
            return

        if emoji not in msg.reactions:
            msg.reactions[emoji] = []

        if current_user.username in msg.reactions[emoji]:
            msg.reactions[emoji].remove(current_user.username)
        else:
            msg.reactions[emoji].append(current_user.username)

        react_msg = Message(
            username=current_user.username,
            text=emoji,
            room_id=topic,
            msg_type="react",
            id=message.id,
            reactions=dict(msg.reactions),
        )

        if is_private:
            pubsub_service.broadcast_to_private(page, topic, react_msg)
        else:
            pubsub_service.broadcast_to_room(page, topic, react_msg)

        rebuild_bubble(message.id)

    # ── Handler central de mensagens ──────────────────

    def on_message_received(topic, message):
        if message.msg_type == "edit":
            if message.id in messages_store:
                messages_store[message.id].text = message.text
                messages_store[message.id].is_edited = True
                rebuild_bubble(message.id)

        elif message.msg_type == "delete":
            if message.id in messages_store:
                messages_store[message.id].is_deleted = True
                rebuild_bubble(message.id)

        elif message.msg_type == "react":
            if message.id in messages_store:
                messages_store[message.id].reactions = message.reactions
                rebuild_bubble(message.id)

        else:
            # Nova mensagem (chat, login, sticker)
            bubble = MessageBubble(
                message, current_user, page,
                on_edit=handle_edit,
                on_delete=handle_delete,
                on_react=handle_react,
            )

            if message.msg_type != "login":
                messages_store[message.id] = message
                bubble_map[message.id] = bubble

            messages_list.controls.append(bubble)
            page.update()

    # ── Envio de mensagens ────────────────────────────

    def send_message(e, file_path=None, sticker=None):
        text = new_message.value.strip()

        if not text and not file_path and not sticker:
            return

        msg = Message(
            username=current_user.username,
            text=sticker if sticker else text,
            room_id=topic,
            file_path=file_path,
            msg_type="sticker" if sticker else "chat",
        )

        if is_private:
            pubsub_service.broadcast_to_private(page, topic, msg)
        else:
            pubsub_service.broadcast_to_room(page, topic, msg)

        new_message.value = ""
        page.update()

    # ── Dialog de ficheiro ────────────────────────────

    def show_file_dialog(e):
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
                path_field.error_text = "Insere o caminho"
                page.update()
                return
            saved = file_service.save_file(path)
            if saved:
                dialog.open = False
                page.update()
                send_message(None, file_path=saved)
            else:
                path_field.error_text = "Ficheiro não encontrado"
                page.update()

        def close(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Enviar ficheiro"),
            content=ft.Column(
                controls=[
                    ft.Text("Cola o caminho completo do ficheiro:", size=13, color=ft.Colors.GREY_600),
                    path_field,
                ],
                tight=True,
                spacing=12,
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=close),
                ft.TextButton("Enviar", on_click=send_file),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ── Dialog de stickers ────────────────────────────

    def show_sticker_picker(e):
        def send_sticker(emoji):
            dialog.open = False
            page.update()
            send_message(None, sticker=emoji)

        def close(e):
            dialog.open = False
            page.update()

        grid = ft.GridView(
            runs_count=6,
            max_extent=56,
            spacing=6,
            run_spacing=6,
            height=200,
        )

        for emoji in DEFAULT_STICKERS:
            grid.controls.append(
                ft.Container(
                    content=ft.Text(emoji, size=30, text_align=ft.TextAlign.CENTER),
                    on_click=lambda e, em=emoji: send_sticker(em),
                    border_radius=8,
                    padding=ft.padding.all(4),
                    ink=True,
                )
            )

        dialog = ft.AlertDialog(
            title=ft.Text("Escolhe um sticker"),
            content=grid,
            actions=[ft.TextButton("Fechar", on_click=close)],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    # ── Subscrição ────────────────────────────────────

    if is_private:
        pubsub_service.subscribe_to_private(page, topic, on_message_received)
    else:
        pubsub_service.subscribe_to_room(page, topic, on_message_received)
        pubsub_service.broadcast_to_room(
            page, topic,
            Message(
                username=current_user.username,
                text=f"{current_user.username} entrou em #{chat_name} 👋",
                room_id=topic,
                msg_type="login",
            ),
        )

    # ── Botões da barra de envio ──────────────────────

    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        icon_color=ft.Colors.BLUE_600,
        tooltip="Enviar",
        on_click=send_message,
    )

    attach_button = ft.IconButton(
        icon=ft.Icons.ATTACH_FILE,
        icon_color=ft.Colors.GREY_600,
        tooltip="Enviar ficheiro",
        on_click=show_file_dialog,
    )

    sticker_button = ft.IconButton(
        icon=ft.Icons.EMOJI_EMOTIONS,
        icon_color=ft.Colors.GREY_600,
        tooltip="Stickers",
        on_click=show_sticker_picker,
    )

    # ── Cabeçalho ────────────────────────────────────

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
                        ft.Text(private_user["username"], size=15, weight=ft.FontWeight.BOLD),
                        ft.Text("Mensagem direta", size=11, color=ft.Colors.GREY_500),
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
            controls=[attach_button, sticker_button, new_message, send_button],
            spacing=4,
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