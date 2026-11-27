import datetime
from typing import Any, Callable
from src.core.filter_type_enum import filter_type_enum


class filter_comparator_wrapper:
    """Обертка над функцией сравнения, поддерживающая как вызов fn(...), так и метод compare(...)"""

    def __init__(self, fn: Callable[[Any, Any], bool]):
        self._fn = fn

    def compare(self, actual: Any, expected: Any) -> bool:
        return self._fn(actual, expected)

    def __call__(self, actual: Any, expected: Any) -> bool:
        return self._fn(actual, expected)


class filter_comparator_factory:
    """
    Фабрика операций сравнения для фильтрации данных.
    Инкапсулирует стратегии проверки условий (EQUALS, LIKE, >, <, >=, <=) в одном месте.
    """

    def __init__(self):
        self.__comparators: dict[filter_type_enum, Callable[[Any, Any], bool]] = {
            filter_type_enum.EQUALS: self._compare_equals,
            filter_type_enum.LIKE: self._compare_like,
            filter_type_enum.GREATER_THAN: lambda a, b: self._compare_order(a, b, lambda x, y: x > y),
            filter_type_enum.LESS_THAN: lambda a, b: self._compare_order(a, b, lambda x, y: x < y),
            filter_type_enum.GREATER_EQUAL: lambda a, b: self._compare_order(a, b, lambda x, y: x >= y),
            filter_type_enum.LESS_EQUAL: lambda a, b: self._compare_order(a, b, lambda x, y: x <= y),
        }

    def create(self, op: filter_type_enum) -> filter_comparator_wrapper:
        """
        Получить компаратор для заданной операции фильтрации
        """
        if not isinstance(op, filter_type_enum):
            op = filter_type_enum.from_string(str(op))

        fn = self.__comparators.get(op, self._compare_equals)
        return filter_comparator_wrapper(fn)

    @staticmethod
    def _unwrap(val: Any) -> Any:
        return getattr(val, "value", val)

    @classmethod
    def _compare_equals(cls, actual: Any, expected: Any) -> bool:
        if actual is None:
            return False
        act, exp = cls._coerce(actual, expected)
        act = cls._unwrap(act)
        exp = cls._unwrap(exp)
        if isinstance(act, str) and isinstance(exp, str):
            return act.strip() == exp.strip()
        return act == exp or str(act).strip() == str(exp).strip()

    @classmethod
    def _compare_like(cls, actual: Any, expected: Any) -> bool:
        if actual is None:
            return False
        act = cls._unwrap(actual)
        exp = cls._unwrap(expected)
        return str(exp).strip().lower() in str(act).lower()

    @classmethod
    def _compare_order(cls, actual: Any, expected: Any, comp_fn: Callable) -> bool:
        if actual is None:
            return False
        act, exp = cls._coerce(actual, expected)
        try:
            return comp_fn(act, exp)
        except TypeError:
            return False

    @classmethod
    def _coerce(cls, actual: Any, expected: Any) -> tuple:
        """Приведение значений к сопоставимым типам (даты, числа)"""
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

        if isinstance(actual, (int, float)) and not isinstance(actual, bool):
            try:
                return float(actual), float(expected)
            except (ValueError, TypeError):
                pass

        return actual, expected
