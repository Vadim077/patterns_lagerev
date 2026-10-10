from src.core.entity_model import entity_model


class storage_model(entity_model):
    """Модель склада"""

    def __init__(self, name: str = None) -> None:
        """Конструктор склада."""
        super().__init__(name=name)

    """
    Фабричный метод: Основной склад
    """
    @staticmethod
    def create_main() -> "storage_model":
        return storage_model(name="Основной склад")

    """
    Фабричный метод: Холодильник
    """
    @staticmethod
    def create_cold() -> "storage_model":
        return storage_model(name="Холодильник")