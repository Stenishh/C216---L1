from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.items import ItemModel
from src.schemas.items import ItemCreate


class ItemRepository:
    def __init__(self, session: Session):
        self.session = session

    def list(self):
        return self.session.scalars(select(ItemModel).order_by(ItemModel.id)).all()

    def exists(self, name: str):
        return (
            self.session.scalar(select(ItemModel.id).where(ItemModel.name == name))
            is not None
        )

    def create(self, data: ItemCreate):
        item = ItemModel(**data.model_dump())
        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item
