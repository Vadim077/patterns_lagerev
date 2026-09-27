class arguments_exception(Exception):
    def __init__(self, field: str = "", message: str = "", stack_trace: str = ""):
        self.__field: str = str(field).strip() if field else ""
        self.__message: str = str(message).strip() if message else ""
        self.__stack_trace: str = str(stack_trace).strip() if stack_trace else ""
        super().__init__(self.__message)

    @property
    def field(self) -> str:
        return self.__field

    @property
    def message(self) -> str:
        return self.__message

    def __str__(self) -> str:
        return f"Ошибка: Некорректный аргумент! [{self.__field}]\n{self.__message}\n{self.__stack_trace}"