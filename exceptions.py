class StatusCodeNotOK(Exception):
    """Статус отличается от 200."""

    pass


class JSONDecodeError(Exception):
    """Ошибка преобразования к типам данных Python."""

    pass
