from typing import Any, Optional
from src.core.abstract_deserializer import abstract_deserializer


class basic_deserializer(abstract_deserializer):
    """
    Десериализатор простых типов данных
    """

    def deserialize(self, data: Any, target_type: Optional[type] = None) -> Any:
        """
        Преобразование примитивных типов
        """
        if data is None:
            return None

        # Если явно передан ожидаемый тип — выполняем приведение
        if target_type is not None and not isinstance(data, target_type):
            return target_type(data)

        return data