from sqlalchemy.exc import IntegrityError

from src.repositories.items import ItemRepository
from src.schemas.items import ItemCreate


class DuplicateItem(ValueError):
    pass


class ItemService:
    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def list(self):
        return self.repository.list()

    def create(self, data: ItemCreate):
        try:
            return self.repository.create(data)
        except IntegrityError as exc:
            self.repository.session.rollback()
            if not self.repository.exists(data.name):
                raise
            raise DuplicateItem("Já existe um item com esse nome") from exc
