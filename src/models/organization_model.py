from src.core.entity_model import entity_model
from src.core.exception import arguments_exception


class organization_model(entity_model):
    """
    Модель организации.
    Содержит: ИНН, БИК, расчетный счет, форму собственности.
    """

    def __init__(
        self,
        name: str = None,
        inn: str = None,
        bik: str = None,
        account: str = None,
        ownership_type: str = None,
    ) -> None:
        """Конструктор организации."""
        super().__init__(name=name)
        self._inn: str = ""
        self._bik: str = ""
        self._account: str = ""
        self._ownership_type: str = ""

        if inn is not None:
            self.inn = inn
        if bik is not None:
            self.bik = bik
        if account is not None:
            self.account = account
        if ownership_type is not None:
            self.ownership_type = ownership_type

    @property
    def inn(self) -> str:
        """Получить ИНН."""
        return self._inn

    @inn.setter
    def inn(self, value: str) -> None:
        """Установить ИНН (строго 10 или 12 цифр)."""
        if not value or not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) not in (10, 12):
            raise arguments_exception(
                field="inn",
                message="ИНН должен содержать ровно 10 (юр. лицо) или 12 (ИП) цифр",
            )
        self._inn = value.strip()

    @property
    def bik(self) -> str:
        """Получить БИК."""
        return self._bik

    @bik.setter
    def bik(self, value: str) -> None:
        """Установить БИК (строго 9 цифр)."""
        if not value or not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) != 9:
            raise arguments_exception(
                field="bik",
                message="БИК банка должен содержать ровно 9 цифр",
            )
        self._bik = value.strip()

    @property
    def account(self) -> str:
        """Получить расчетный счет."""
        return self._account

    @account.setter
    def account(self, value: str) -> None:
        """Установить расчетный счет (строго 20 цифр)."""
        if not value or not isinstance(value, str) or not value.strip().isdigit() or len(value.strip()) != 20:
            raise arguments_exception(
                field="account",
                message="Расчетный счет должен содержать ровно 20 цифр",
            )
        self._account = value.strip()

    @property
    def ownership_type(self) -> str:
        """Получить форму собственности (например, 'ООО', 'ПАО', 'ИП')."""
        return self._ownership_type

    @ownership_type.setter
    def ownership_type(self, value: str) -> None:
        """Установить форму собственности (непустая строка не длиннее 10 символов)."""
        if not value or not isinstance(value, str) or not value.strip():
            raise arguments_exception(
                field="ownership_type",
                message="Форма собственности не может быть пустой",
            )
        cleaned = value.strip()
        if len(cleaned) > 10:
            raise arguments_exception(
                field="ownership_type",
                message="Форма собственности не должна превышать 10 символов",
            )
        self._ownership_type = cleaned