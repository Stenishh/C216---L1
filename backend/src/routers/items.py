from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.repositories.items import ItemRepository
from src.schemas.items import ItemCreate, ItemRead
from src.services.items import DuplicateItem, ItemService

router = APIRouter(prefix="/items", tags=["Itens"])


def get_service(session: Annotated[Session, Depends(get_db)]):
    return ItemService(ItemRepository(session))


Service = Annotated[ItemService, Depends(get_service)]


@router.get("/", response_model=list[ItemRead])
def list_items(service: Service):
    return service.list()


@router.post("/", response_model=ItemRead, status_code=201)
def create_item(data: ItemCreate, service: Service):
    try:
        return service.create(data)
    except DuplicateItem as exc:
        raise HTTPException(409, str(exc)) from exc
