from src.core.entity_model import entity_model


class storage_model(entity_model):
    """Модель склада"""

    def __init__(self, name: str = None) -> None:
        """Конструктор склада."""
        super().__init__(name=name)