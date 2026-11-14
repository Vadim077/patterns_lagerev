from src.models import (
    nomenclature_group_model,
    nomenclature_model,
    range_model,
    recipe_model,
    storage_model,
)


class entity_factory:
    """Фабрика разрешённых доменных сущностей REST API"""

    def __init__(self) -> None:
        self.__models: dict[str, type] = {
            "range_model": range_model,
            "nomenclature_group_model": nomenclature_group_model,
            "storage_model": storage_model,
            "nomenclature_model": nomenclature_model,
            "recipe_model": recipe_model,
        }

    def get_model_class(self, entity_type: str) -> type:
        """Возвращает класс модели по строковому типу"""
        if not isinstance(entity_type, str) or not entity_type.strip():
            raise ValueError("Тип сущности не может быть пустым")

        model_class = self.__models.get(entity_type.strip().lower())

        if model_class is None:
            raise ValueError(
                f"Неподдерживаемый тип сущности: {entity_type}"
            )

        return model_class

    def get_supported_types(self) -> tuple[str, ...]:
        """Возвращает список поддерживаемых типов сущностей"""
        return tuple(self.__models.keys())