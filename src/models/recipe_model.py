from src.core.abstract_model import abstract_model
from src.core.exception import arguments_exception
from src.models.nomenclature_model import nomenclature_model
from src.models.recipe_row_model import recipe_row_model


"""
Модель технологической карты (рецепта)
"""
class recipe_model(abstract_model):

    def __init__(
        self,
        name: str = "",
        dish: nomenclature_model = None,
        cooking_time: int = 0,
        instructions: list = None,
        portions: int = 1,
    ) -> None:
        super().__init__(name=name)
        self.__dish: nomenclature_model = None
        self.__rows: list[recipe_row_model] = []
        self.__cooking_time: int = 0
        self.__instructions: list[str] = []
        self.__portions: int = 1

        if dish is not None:
            self.dish = dish
        self.cooking_time = cooking_time
        self.instructions = instructions or []
        self.portions = portions

    """
    Целевое блюдо или полуфабрикат
    """
    @property
    def dish(self) -> nomenclature_model:
        return self.__dish

    @dish.setter
    def dish(self, value: nomenclature_model) -> None:
        if not isinstance(value, nomenclature_model):
            raise arguments_exception(field="dish", message="Некорректная номенклатура блюда")
        self.__dish = value
        if not self.name:
            self.name = value.name

    """
    Список строк технологической карты
    """
    @property
    def rows(self) -> list:
        return self.__rows
    @property
    def items(self) -> list:
        return self.__rows

    """
    Время приготовления в минутах
    """
    @property
    def cooking_time(self) -> int:
        return self.__cooking_time

    @cooking_time.setter
    def cooking_time(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise arguments_exception(field="cooking_time", message="Время приготовления должно быть неотрицательным")
        self.__cooking_time = value

    """
    Шаги технологического процесса
    """
    @property
    def instructions(self) -> list:
        return self.__instructions

    @instructions.setter
    def instructions(self, value: list) -> None:
        if not isinstance(value, list):
            raise arguments_exception(field="instructions", message="Инструкции должны быть списком")
        self.__instructions = [str(step).strip() for step in value]

    """
    Количество порций
    """
    @property
    def portions(self) -> int:
        return self.__portions

    @portions.setter
    def portions(self, value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise arguments_exception(field="portions", message="Количество порций должно быть больше нуля")
        self.__portions = value

    """
    Добавить ингредиент или полуфабрикат в рецепт
    """
    def add_row(self, row: recipe_row_model) -> bool:
        if not isinstance(row, recipe_row_model):
            raise arguments_exception(field="row", message="Строка рецепта должна быть recipe_row_model")
        self.__rows.append(row)
        return True

    """
    Удалить строку рецепта по объекту или ID
    """
    def remove_row(self, row_or_id) -> bool:
        target_id = row_or_id.id if isinstance(row_or_id, recipe_row_model) else str(row_or_id)
        for i, r in enumerate(self.__rows):
            if r.id == target_id:
                self.__rows.pop(i)
                return True
        return False

    """
    Суммарный вес брутто (включая рекурсивный вес полуфабрикатов)
    """
    @property
    def brutto(self) -> float:
        return round(sum(row.brutto for row in self.__rows), 2)

    """
    Суммарный вес нетто (включая рекурсивный вес полуфабрикатов)
    """
    @property
    def netto(self) -> float:
        return round(sum(row.netto for row in self.__rows), 2)

        """
    Фабричный метод: создать рецепт полуфабриката 'Песочное тесто'
    """
    @staticmethod
    def create_dough_recipe(
        dish: nomenclature_model,
        flour: nomenclature_model,
        butter: nomenclature_model,
        sugar: nomenclature_model,
        egg: nomenclature_model,
    ) -> "recipe_model":
        recipe = recipe_model(
            name="Рецепт: Песочное тесто",
            dish=dish,
            cooking_time=15,
            instructions=[
                "Растереть размягченное сливочное масло с сахаром",
                "Ввести яичный желток, перемешать до однородности",
                "Постепенно ввести муку и быстро замесить тесто",
            ],
            portions=1,
        )
        # Мука: 250 г брутто / 250 г нетто
        recipe.add_row(recipe_row_model.create_ingredient(flour, brutto=250.0, netto=250.0))
        # Масло: 150 г брутто / 150 г нетто
        recipe.add_row(recipe_row_model.create_ingredient(butter, brutto=150.0, netto=150.0))
        # Сахар: 100 г брутто / 100 г нетто
        recipe.add_row(recipe_row_model.create_ingredient(sugar, brutto=100.0, netto=100.0))
        # Яйцо: 60 г брутто (со скорлупой) / 50 г нетто (желток)
        recipe.add_row(recipe_row_model.create_ingredient(egg, brutto=60.0, netto=50.0))
        return recipe

    """
    Фабричный метод: создать рецепт блюда 'Печенье Ромашка' (содержит полуфабрикат и упаковку)
    """
    @staticmethod
    def create_cookie_recipe(
        dish: nomenclature_model,
        dough_nomenclature: nomenclature_model,
        dough_recipe: "recipe_model",
        box_packaging: nomenclature_model,
    ) -> "recipe_model":
        recipe = recipe_model(
            name="Рецепт: Песочное печенье «Ромашка»",
            dish=dish,
            cooking_time=25,
            instructions=[
                "Раскатать полуфабрикат песочного теста в пласт 5 мм",
                "Вырезать печенье в форме ромашки",
                "Выпекать в печи при 180 °C в течение 12-15 минут",
                "Охладить и упаковать в крафтовую коробку",
            ],
            portions=10,
        )
        # Полуфабрикат (блюдо в блюде): вес берется рекурсивно из dough_recipe
        recipe.add_row(recipe_row_model.create_semi_finished(dough_nomenclature, sub_recipe=dough_recipe))
        # Упаковка: 20 г брутто (вес коробки) / 0 г нетто (тара не съедобна)
        recipe.add_row(recipe_row_model.create_ingredient(box_packaging, brutto=20.0, netto=0.0))
        return recipe