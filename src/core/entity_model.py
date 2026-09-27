from src.core.abstract_model import name_id

"""
Общий класс для наследования. Содержит стандартное определение: код, наименование
"""
class entity_model(name_id):

    def __init__(self, name: str = None) -> None:
        super().__init__(name=name)