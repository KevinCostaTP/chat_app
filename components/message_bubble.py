# components/message_bubble.py

import flet as ft


def MessageBubble(message, current_user):

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

  
    bubble = ft.Container(
    content=ft.Text(
        message.text,
        color=ft.Colors.WHITE if is_mine else ft.Colors.BLACK87,
        size=14,
        selectable=True,
        width=260,  # limita a largura do texto em vez do container
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