from src.core.entity_model import entity_model


class nomenclature_group_model(entity_model):
    """Модель группы номенклатуры. """

    def __init__(self, name: str = None) -> None:
        """Конструктор группы номенклатуры."""
        super().__init__(name=name)