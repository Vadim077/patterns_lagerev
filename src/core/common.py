import datetime
from typing import Any
from src.core.abstract_model import abstract_model
from src.core.filter_type_enum import filter_type_enum
from src.core.validator import validator, arguments_exception


"""
Набор общих статических методов для рефлексии и инспекции моделей
"""
class common:

    """
    Получить полный список публичных свойств любой модели
    """
    @staticmethod
    def get_fields(source, is_common: bool = False) -> list:
        if source is None:
            return []

        items = list(filter(lambda x: not x.startswith("_"), dir(source)))
        result = []

        for item in items:
            attribute = getattr(source.__class__, item, None)

            if isinstance(attribute, property):
                try:
                    value = getattr(source, item)
                except Exception:
                    continue

                if is_common is True and (isinstance(value, dict) or isinstance(value, (list, tuple))):
                    continue

                result.append(item)

        return result

    """
    Получить все зависимые доменные сущности через рефлексию
    """
    @staticmethod
    def get_references(source, visited: set = None) -> list:
        if source is None:
            return []

        visited = visited or set()
        source_id = id(source)
        if source_id in visited:
            return []
        visited.add(source_id)

        references = []
        fields = common.get_fields(source, is_common=False)

        for field in fields:
            try:
                value = getattr(source, field)
            except Exception:
                continue

            if value is None or value is source:
                continue

            if isinstance(value, abstract_model):
                references.append(value)
                references.extend(common.get_references(value, visited))
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, abstract_model) and item is not source:
                        references.append(item)
                        references.extend(common.get_references(item, visited))
                    elif hasattr(item, "__dict__"):
                        references.extend(common.get_references(item, visited))

        return references

    """
    Возвращает словарь всех доступных ключей и их описаний
    через статические методы с суффиксом '_key'
    """
    @staticmethod
    def domains(source: object) -> dict:
        result = {}

        method_names = [
            name for name in dir(source)
            if callable(getattr(source, name)) and name.endswith("_key")
        ]

        for method_name in method_names:
            method = getattr(source, method_name)
            key_value = method()
            docstring = method.__doc__
            description = docstring.strip().split("\n")[0] if docstring else method_name
            result[key_value] = description

        return dict(sorted(result.items()))

    """
    Получить значения по точечному пути (поддерживает вложенные объекты и списки)
    """
    @staticmethod
    def get_values_by_path(source: object, field_path: str) -> list:
        if source is None or not field_path:
            return []

        parts = field_path.strip().split(".")
        current_items = [source]

        for part in parts:
            next_items = []
            for item in current_items:
                if item is None:
                    continue

                if isinstance(item, (list, tuple)):
                    for sub_item in item:
                        if sub_item is None:
                            continue
                        if hasattr(sub_item, part):
                            val = getattr(sub_item, part)
                            if isinstance(val, (list, tuple)):
                                next_items.extend(val)
                            else:
                                next_items.append(val)
                        elif isinstance(sub_item, dict) and part in sub_item:
                            val = sub_item[part]
                            if isinstance(val, (list, tuple)):
                                next_items.extend(val)
                            else:
                                next_items.append(val)
                else:
                    if hasattr(item, part):
                        val = getattr(item, part)
                        if isinstance(val, (list, tuple)):
                            next_items.extend(val)
                        else:
                            next_items.append(val)
                    elif isinstance(item, dict) and part in item:
                        val = item[part]
                        if isinstance(val, (list, tuple)):
                            next_items.extend(val)
                        else:
                            next_items.append(val)

            current_items = next_items

        return current_items

    """
    Проверить соответствие значения условию фильтрации
    """
    @staticmethod
    def match_value(actual: Any, expected: Any, op: filter_type_enum) -> bool:
        if actual is None:
            return False

        if not isinstance(op, filter_type_enum):
            op = filter_type_enum.from_string(str(op))

        # Обработка строковых операций
        if op == filter_type_enum.LIKE:
            actual_str = actual.value if hasattr(actual, "value") else str(actual)
            expected_str = expected.value if hasattr(expected, "value") else str(expected)
            return expected_str.strip().lower() in actual_str.lower()

        # Попытка парсинга дат
        actual_val, expected_val = common.__coerce_comparable(actual, expected)

        if op == filter_type_enum.EQUALS:
            if isinstance(actual_val, str) and isinstance(expected_val, str):
                return actual_val.strip() == expected_val.strip()
            if actual_val == expected_val:
                return True
            # Поддержка Enum (сравнение по значению перечисления)
            if hasattr(actual_val, "value") and actual_val.value == expected_val:
                return True
            if hasattr(expected_val, "value") and actual_val == expected_val.value:
                return True
            # Строковое приведение (например, UUID со строкой)
            if str(actual_val).strip() == str(expected_val).strip():
                return True
            return False

        try:
            if op == filter_type_enum.GREATER_THAN:
                return actual_val > expected_val
            if op == filter_type_enum.LESS_THAN:
                return actual_val < expected_val
            if op == filter_type_enum.GREATER_EQUAL:
                return actual_val >= expected_val
            if op == filter_type_enum.LESS_EQUAL:
                return actual_val <= expected_val
        except TypeError:
            return False

        return False

    @staticmethod
    def __coerce_comparable(actual: Any, expected: Any) -> tuple:
        """Приведение значений к сопоставимым типам (даты, числа)"""
        # Если actual - дата или datetime
        if isinstance(actual, (datetime.datetime, datetime.date)):
            if isinstance(expected, str):
                try:
                    exp_dt = datetime.datetime.fromisoformat(expected.strip())
                    act_dt = actual if isinstance(actual, datetime.datetime) else datetime.datetime.combine(actual, datetime.time.min)
                    return act_dt, exp_dt
                except Exception:
                    try:
                        exp_d = datetime.date.fromisoformat(expected.strip())
                        act_d = actual.date() if isinstance(actual, datetime.datetime) else actual
                        return act_d, exp_d
                    except Exception:
                        pass
            elif isinstance(expected, datetime.datetime):
                act_dt = actual if isinstance(actual, datetime.datetime) else datetime.datetime.combine(actual, datetime.time.min)
                return act_dt, expected
            elif isinstance(expected, datetime.date):
                act_d = actual.date() if isinstance(actual, datetime.datetime) else actual
                return act_d, expected

        # Если actual - число
        if isinstance(actual, (int, float)) and not isinstance(actual, bool):
            try:
                exp_float = float(expected)
                return float(actual), exp_float
            except (ValueError, TypeError):
                pass

        return actual, expected
