from src.core.exception import arguments_exception


class operation_exception(Exception):
    """Исключение при ошибках выполнения операций (например, загрузка и обработка файлов)."""

    def __init__(self, message: str = ""):
        self.__message: str = str(message).strip() if message else ""
        super().__init__(self.__message)

    @property
    def message(self) -> str:
        return self.__message

    def __str__(self) -> str:
        return f"Ошибка операции: {self.__message}"


# Алиас на случай опечатки в названии (в tst/test_settings_manager.py написано operation_exeption)
operation_exeption = operation_exception


class validator:
    """Утилитный класс для централизованной проверки параметров."""

    @staticmethod
    def validate(value: object, field: str = "argument") -> bool:
        """
        Проверить значение на корректность.
        Если пустое или пробельное — выбрасывает arguments_exception.
        """
        if value is None:
            raise arguments_exception(field=field, message="Значение не может быть пустым")
        if isinstance(value, str) and not value.strip():
            raise arguments_exception(field=field, message="Строка не может быть пустой")
        return True