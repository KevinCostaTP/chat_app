# components/message_bubble.py

import flet as ft
from services.file_service import is_image, get_file_name, get_file_size

REACTION_EMOJIS = ["👍", "❤️", "😂", "😮", "😢"]


def MessageBubble(message, current_user, page, on_edit=None, on_delete=None, on_react=None):
    """
    Cria o balão de mensagem com suporte a:
    - Texto normal
    - Ficheiros e imagens
    - Stickers (emoji grandes)
    - Editar e eliminar (só para o autor)
    - Reações por emoji com contagem
    """

    # Mensagem de sistema
    if message.msg_type == "login":
        return ft.Container(
            content=ft.Text(
                message.text,
                italic=True,
                color=ft.Colors.GREY_500,
                size=12,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=4, horizontal=16),
            alignment=ft.Alignment(0, 0),
        )

    is_mine = message.username == current_user.username

    # ── Conteúdo do balão ──────────────────────────────
    bubble_inner = []

    if message.is_deleted:
        bubble_inner.append(
            ft.Text(
                "🚫 Mensagem eliminada",
                italic=True,
                color=ft.Colors.GREY_400,
                size=13,
            )
        )
    else:
        # Sticker — emoji grande, sem fundo
        if message.msg_type == "sticker":
            bubble_inner.append(
                ft.Text(message.text, size=52, text_align=ft.TextAlign.CENTER)
            )
        else:
            # Texto normal
            if message.text:
                edited_suffix = "  ✏️" if message.is_edited else ""
                bubble_inner.append(
                    ft.Text(
                        message.text + edited_suffix,
                        color=ft.Colors.WHITE if is_mine else ft.Colors.BLACK87,
                        size=14,
                        selectable=True,
                        width=260,
                    )
                )

            # Ficheiro ou imagem
            if message.file_path:
                if is_image(message.file_path):
                    bubble_inner.append(
                        ft.Image(
                            src=message.file_path,
                            width=240,
                            height=180,
                            fit="cover",
                            border_radius=8,
                        )
                    )
                else:
                    bubble_inner.append(
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(
                                        ft.Icons.INSERT_DRIVE_FILE,
                                        color=ft.Colors.WHITE if is_mine else ft.Colors.BLUE_600,
                                        size=28,
                                    ),
                                    ft.Column(
                                        controls=[
                                            ft.Text(
                                                get_file_name(message.file_path),
                                                color=ft.Colors.WHITE if is_mine else ft.Colors.BLACK87,
                                                size=13,
                                                weight=ft.FontWeight.W_500,
                                                width=180,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Text(
                                                get_file_size(message.file_path),
                                                color=ft.Colors.WHITE70 if is_mine else ft.Colors.GREY_600,
                                                size=11,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                ],
                                spacing=8,
                            ),
                            padding=ft.padding.all(4),
                        )
                    )

    # Balão
    is_sticker = message.msg_type == "sticker" and not message.is_deleted
    bubble = ft.Container(
        content=ft.Column(controls=bubble_inner, spacing=6),
        bgcolor=ft.Colors.TRANSPARENT if is_sticker else (ft.Colors.BLUE_600 if is_mine else ft.Colors.GREY_200),
        padding=ft.padding.all(4) if is_sticker else ft.padding.symmetric(vertical=8, horizontal=12),
        border_radius=ft.border_radius.only(
            top_left=12, top_right=12,
            bottom_left=0 if is_mine else 12,
            bottom_right=12 if is_mine else 0,
        ),
    )

    # ── Linha de hora e botões ─────────────────────────
    time_controls = [
        ft.Text(message.timestamp.strftime("%H:%M"), size=10, color=ft.Colors.GREY_500)
    ]

    if is_mine and not message.is_deleted:
        if on_edit:
            time_controls.append(
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_size=14,
                    icon_color=ft.Colors.GREY_400,
                    tooltip="Editar",
                    on_click=lambda e, m=message: on_edit(m),
                )
            )
        if on_delete:
            time_controls.append(
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=14,
                    icon_color=ft.Colors.GREY_400,
                    tooltip="Eliminar",
                    on_click=lambda e, m=message: on_delete(m),
                )
            )

    # ── Reações ────────────────────────────────────────
    reaction_controls = []

    if message.reactions and not message.is_deleted:
        for emoji, users in message.reactions.items():
            if users:
                is_reacted = current_user.username in users
                reaction_controls.append(
                    ft.Container(
                        content=ft.Text(f"{emoji} {len(users)}", size=12),
                        bgcolor=ft.Colors.BLUE_100 if is_reacted else ft.Colors.GREY_100,
                        border_radius=12,
                        padding=ft.padding.symmetric(vertical=2, horizontal=8),
                        on_click=lambda e, em=emoji, m=message: on_react(m, em) if on_react else None,
                        ink=True,
                    )
                )

    # Botão para adicionar reação
    if not message.is_deleted and on_react:
        def show_reaction_picker(e, msg=message):
            def pick_emoji(em, m):
                on_react(m, em)
                dialog.open = False
                page.update()

            dialog = ft.AlertDialog(
                title=ft.Text("Adicionar reação"),
                content=ft.Row(
                    controls=[
                        ft.TextButton(
                            em,
                            on_click=lambda e, em=em, m=msg: pick_emoji(em, m),
                        )
                        for em in REACTION_EMOJIS
                    ],
                    spacing=4,
                ),
            )
            page.overlay.append(dialog)
            dialog.open = True
            page.update()

        reaction_controls.append(
            ft.Container(
                content=ft.Text("+ 😊", size=12, color=ft.Colors.GREY_500),
                on_click=show_reaction_picker,
                border_radius=12,
                padding=ft.padding.symmetric(vertical=2, horizontal=6),
                ink=True,
            )
        )

    # ── Montagem final ─────────────────────────────────
    col_controls = []
    if not is_mine:
        col_controls.append(
            ft.Text(message.username, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
        )
    col_controls.append(bubble)
    col_controls.append(ft.Row(controls=time_controls, spacing=2))
    if reaction_controls:
        col_controls.append(ft.Row(controls=reaction_controls, spacing=4, wrap=True))

    content = ft.Column(
        controls=col_controls,
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.END if is_mine else ft.CrossAxisAlignment.START,
    )

    return ft.Container(
        data=message.id,
        content=content,
        padding=ft.padding.symmetric(vertical=4, horizontal=16),
        alignment=ft.Alignment(1, 0) if is_mine else ft.Alignment(-1, 0),
    )