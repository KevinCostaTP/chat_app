# services/pubsub_service.py

# Este ficheiro centraliza toda a lógica de comunicação em tempo real.
# O PubSub é o sistema que permite que as mensagens de um utilizador
# cheguem a todos os outros instantaneamente.


def subscribe(page, handler):
    """
    Subscreve este utilizador para receber mensagens.

    Como funciona:
        - Cada utilizador que abre a app "subscreve" o canal
        - Quando alguém envia uma mensagem, o PubSub chama o 'handler'
          de TODOS os subscritores automaticamente

    Parâmetros:
        page    - a página Flet deste utilizador
        handler - a função que vai ser chamada quando chegar uma mensagem
    """
    page.pubsub.subscribe(handler)


def unsubscribe(page):
    """
    Cancela a subscrição quando o utilizador fecha a app.
    Importante para não continuar a receber mensagens desnecessariamente.
    """
    page.pubsub.unsubscribe_all()


def broadcast(page, message):
    """
    Envia uma mensagem para TODOS os utilizadores subscritos.

    Parâmetros:
        page    - a página Flet de quem está a enviar
        message - objeto Message com os dados da mensagem
    """
    page.pubsub.send_all(message)