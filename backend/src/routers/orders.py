from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.repositories.orders import OrderRepository
from src.schemas.orders import OrderCreate, OrderPatch, OrderRead
from src.services.orders import (
    OrderConflict,
    OrderCustomerNotFound,
    OrderNotFound,
    OrderService,
)

router = APIRouter(prefix="/orders", tags=["Ordens"])
OrderId = Annotated[int, Path(gt=0)]


def get_order_service(session: Annotated[Session, Depends(get_db)]):
    return OrderService(OrderRepository(session))


Service = Annotated[OrderService, Depends(get_order_service)]


def execute(operation, *args):
    try:
        return operation(*args)
    except OrderNotFound as exc:
        raise HTTPException(404, "Ordem não encontrada.") from exc
    except OrderCustomerNotFound as exc:
        raise HTTPException(404, "Cliente não encontrado.") from exc
    except OrderConflict as exc:
        raise HTTPException(409, str(exc)) from exc


@router.post("/", response_model=OrderRead, status_code=201)
def create_order(data: OrderCreate, service: Service, response: Response):
    order = execute(service.create, data)
    response.headers["Location"] = f"/orders/{order.id}"
    return order


@router.get("/", response_model=list[OrderRead])
def list_orders(
    service: Service,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list(offset, limit)


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: OrderId, service: Service):
    return execute(service.get, order_id)


@router.put("/{order_id}", response_model=OrderRead)
def replace_order(order_id: OrderId, data: OrderCreate, service: Service):
    return execute(service.update, order_id, data)


@router.patch("/{order_id}", response_model=OrderRead)
def patch_order(order_id: OrderId, data: OrderPatch, service: Service):
    return execute(service.update, order_id, data)


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: OrderId, service: Service):
    execute(service.delete, order_id)
    return Response(status_code=204)
