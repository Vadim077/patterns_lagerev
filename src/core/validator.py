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


operation_exeption = operation_exception

class validator:
    """Утилитный класс для централизованной проверки параметров."""

    @staticmethod
    def validate(value: object, field_or_type: object = "argument") -> bool:
        """
        Проверить значение на корректность и тип.
        """
        if value is None:
            raise arguments_exception(field=str(field_or_type), message="Значение не может быть пустым")
        
        # Если передан ожидаемый тип (например, str, list, recipe_model)
        if isinstance(field_or_type, type):
            if not isinstance(value, field_or_type):
                raise arguments_exception(
                    field=field_or_type.__name__,
                    message=f"Некорректный тип: ожидается {field_or_type.__name__}, получен {type(value).__name__}",
                )
        
        if isinstance(value, str) and not value.strip():
            raise arguments_exception(field=str(field_or_type), message="Строка не может быть пустой")
        return True