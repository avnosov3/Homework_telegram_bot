class StatusCodeNotOK(Exception):
    """Статус отличается от 200."""

    pass


class JSONWithError(Exception):
    """Ошибка от сервера."""

    pass


class MessageError(Exception):
    """Не удалось отправить сообщение."""

    pass


class ParseError(Exception):
    """Не подходящий параметр."""

    pass
