from abc import ABC
import uuid

class name_id(ABC):

    def __init__(self):
        self.__name = ""
        self.__id = uuid.uuid4()

    @property
    def id(self):
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, new_name: str):
        if new_name is not None and len(new_name) > 0:
            self.__name = new_name
        else:
            raise ValueError("Имя не должно быть пустым")