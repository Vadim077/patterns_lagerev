from src.core.entity_model import entity_model


class nomenclature_group_model(entity_model):
    """Модель группы номенклатуры. """

    def __init__(self, name: str = None) -> None:
        """Конструктор группы номенклатуры."""
        super().__init__(name=name)

    """
    Фабричный метод: группа Сырье
    """
    @staticmethod
    def create_raw() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Сырье")

    """
    Фабричный метод: группа Ингредиенты
    """
    @staticmethod
    def create_ingredients() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Ингредиенты")

    """
    Фабричный метод: группа Полуфабрикаты
    """
    @staticmethod
    def create_semi_finished() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Полуфабрикаты")

    """
    Фабричный метод: группа Готовая продукция
    """
    @staticmethod
    def create_products() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Готовая продукция")

    """
    Фабричный метод: группа Упаковка
    """
    @staticmethod
    def create_packaging() -> "nomenclature_group_model":
        return nomenclature_group_model(name="Упаковка")