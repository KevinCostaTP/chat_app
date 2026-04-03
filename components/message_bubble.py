# components/message_bubble.py

import flet as ft
from services.file_service import is_image, get_file_name, get_file_size


def MessageBubble(message, current_user):
    """
    Cria o balão visual de uma mensagem.
    Suporta mensagens de texto, imagens e ficheiros.
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

    # Lista de conteúdos do bubble (texto e/ou ficheiro)
    bubble_contents = []

    # Se tiver texto, adiciona o texto
    if message.text:
        bubble_contents.append(
            ft.Text(
                message.text,
                color=ft.Colors.WHITE if is_mine else ft.Colors.BLACK87,
                size=14,
                selectable=True,
                width=260,
            )
        )

    # Se tiver ficheiro, adiciona o preview
    if message.file_path:
        if is_image(message.file_path):
            # Preview de imagem
            bubble_contents.append(
                ft.Container(
                    content=ft.Image(
                        src=message.file_path,
                        width=240,
                        height=180,
                        fit=ft.ImageFit.COVER,
                        border_radius=8,
                    ),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
            )
        else:
            # Cartão para outros tipos de ficheiro
            bubble_contents.append(
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
                    padding=ft.padding.all(8),
                    bgcolor=(
                        ft.Colors.BLUE_700 if is_mine
                        else ft.Colors.GREY_100
                    ),
                    border_radius=8,
                )
            )

    # O balão em si
    bubble = ft.Container(
        content=ft.Column(
            controls=bubble_contents,
            spacing=6,
        ),
        bgcolor=ft.Colors.BLUE_600 if is_mine else ft.Colors.GREY_200,
        padding=ft.padding.symmetric(vertical=8, horizontal=12),
        border_radius=ft.border_radius.only(
            top_left=12,
            top_right=12,
            bottom_left=0 if is_mine else 12,
            bottom_right=12 if is_mine else 0,
        ),
    )

    time_text = ft.Text(
        message.timestamp.strftime("%H:%M"),
        size=10,
        color=ft.Colors.GREY_500,
    )

    sender_name = ft.Text(
        message.username,
        size=11,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.BLUE_400,
    )

    content = ft.Column(
        controls=(
            [sender_name, bubble, time_text]
            if not is_mine
            else [bubble, time_text]
        ),
        spacing=2,
        horizontal_alignment=(
            ft.CrossAxisAlignment.END if is_mine
            else ft.CrossAxisAlignment.START
        ),
    )

    return ft.Container(
        content=content,
        padding=ft.padding.symmetric(vertical=4, horizontal=16),
        alignment=ft.Alignment(1, 0) if is_mine else ft.Alignment(-1, 0),
    )