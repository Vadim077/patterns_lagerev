from src.core.abstract_model import abstract_model
from src.core.exception import arguments_exception
from src.core.validator import validator
from src.models.nomenclature_model import nomenclature_model
from src.models.range_model import range_model


"""
Модель строки технологической карты (ингредиент или полуфабрикат)
"""
class recipe_row_model(abstract_model):

    def __init__(
        self,
        nomenclature: nomenclature_model = None,
        brutto: float = 0.0,
        netto: float = None,
        range_unit: range_model = None,
        sub_recipe = None,
    ) -> None:
        super().__init__(name=nomenclature.name if nomenclature else "")
        self.__nomenclature: nomenclature_model = None
        self.__range: range_model = None
        self.__brutto: float = 0.0
        self.__netto: float = 0.0
        self.__sub_recipe = None

        if nomenclature is not None:
            self.nomenclature = nomenclature
        if range_unit is not None:
            self.range = range_unit
        elif nomenclature is not None and getattr(nomenclature, "range", None):
            self.range = nomenclature.range

        self.brutto = brutto
        self.netto = netto if netto is not None else brutto
        self.sub_recipe = sub_recipe

    """
    Номенклатура ингредиента
    """
    @property
    def nomenclature(self) -> nomenclature_model:
        return self.__nomenclature

    @nomenclature.setter
    def nomenclature(self, value: nomenclature_model) -> None:
        if not isinstance(value, nomenclature_model):
            raise arguments_exception(field="nomenclature", message="Некорректная номенклатура")
        self.__nomenclature = value
        self.name = value.name

    """
    Единица измерения
    """
    @property
    def range(self) -> range_model:
        return self.__range

    @range.setter
    def range(self, value: range_model) -> None:
        if value is not None and not isinstance(value, range_model):
            raise arguments_exception(field="range", message="Некорректная единица измерения")
        self.__range = value

    """
    Вложенный рецепт (полуфабрикат)
    """
    @property
    def sub_recipe(self):
        return self.__sub_recipe

    @sub_recipe.setter
    def sub_recipe(self, value) -> None:
        if value is not None and not hasattr(value, "brutto"):
            raise arguments_exception(field="sub_recipe", message="Полуфабрикат должен быть объектом рецепта")
        self.__sub_recipe = value

    """
    Вес брутто (рекурсивный расчет при наличии полуфабриката)
    """
    @property
    def brutto(self) -> float:
        if self.__sub_recipe is not None:
            return float(self.__sub_recipe.brutto)
        return self.__brutto

    @brutto.setter
    def brutto(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise arguments_exception(field="brutto", message="Вес брутто должен быть неотрицательным числом")
        self.__brutto = float(value)

    """
    Вес нетто (рекурсивный расчет при наличии полуфабриката)
    """
    @property
    def netto(self) -> float:
        if self.__sub_recipe is not None:
            return float(self.__sub_recipe.netto)
        return self.__netto

    @netto.setter
    def netto(self, value: float) -> None:
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise arguments_exception(field="netto", message="Вес нетто должен быть неотрицательным числом")
        self.__netto = float(value)

    """
    Фабричный метод: создать строку обычного ингредиента
    """
    @staticmethod
    def create_ingredient(
        nomenclature: nomenclature_model,
        brutto: float,
        netto: float = None,
        range_unit: range_model = None,
    ) -> "recipe_row_model":
        return recipe_row_model(
            nomenclature=nomenclature,
            brutto=brutto,
            netto=netto,
            range_unit=range_unit,
        )

    """
    Фабричный метод: создать строку полуфабриката (блюдо в блюде)
    """
    @staticmethod
    def create_semi_finished(
        nomenclature: nomenclature_model,
        sub_recipe,
        range_unit: range_model = None,
    ) -> "recipe_row_model":
        return recipe_row_model(
            nomenclature=nomenclature,
            brutto=0.0,
            netto=0.0,
            range_unit=range_unit,
            sub_recipe=sub_recipe,
        )