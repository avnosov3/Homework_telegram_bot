class StatusCodeNotOK(Exception):
    """Статус отличается от 200."""

    pass


class JSONWithError(Exception):
    """Ошибка от сервера."""

    pass


class HomeworksWithoutKeys(Exception):
    """В домашней работе нет ключей, которые указаны в документации."""

    pass
