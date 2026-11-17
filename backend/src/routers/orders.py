from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.repositories.orders import OrderRepository
from src.schemas.orders import (
    BudgetRejection,
    DeliveryConfirmation,
    DiagnosisPatch,
    OrderCancellation,
    OrderCreate,
    OrderEventRead,
    OrderPatch,
    OrderRead,
    RepairPatch,
)
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


@router.post("/{order_id}/begin-diagnosis", response_model=OrderRead)
def begin_diagnosis(order_id: OrderId, service: Service):
    return execute(service.begin_diagnosis, order_id)


@router.patch("/{order_id}/diagnosis", response_model=OrderRead)
def update_diagnosis(order_id: OrderId, data: DiagnosisPatch, service: Service):
    return execute(service.update_diagnosis, order_id, data)


@router.post("/{order_id}/request-approval", response_model=OrderRead)
def request_approval(order_id: OrderId, service: Service):
    return execute(service.request_approval, order_id)


@router.post("/{order_id}/approve-budget", response_model=OrderRead)
def approve_budget(order_id: OrderId, service: Service):
    return execute(service.approve_budget, order_id)


@router.post("/{order_id}/reject-budget", response_model=OrderRead)
def reject_budget(order_id: OrderId, data: BudgetRejection, service: Service):
    return execute(service.reject_budget, order_id, data)


@router.post("/{order_id}/start-repair", response_model=OrderRead)
def start_repair(order_id: OrderId, service: Service):
    return execute(service.start_repair, order_id)


@router.patch("/{order_id}/repair", response_model=OrderRead)
def update_repair(order_id: OrderId, data: RepairPatch, service: Service):
    return execute(service.update_repair, order_id, data)


@router.post("/{order_id}/complete-repair", response_model=OrderRead)
def complete_repair(order_id: OrderId, service: Service):
    return execute(service.complete_repair, order_id)


@router.post("/{order_id}/deliver", response_model=OrderRead)
def deliver(order_id: OrderId, data: DeliveryConfirmation, service: Service):
    return execute(service.deliver, order_id)


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel(order_id: OrderId, data: OrderCancellation, service: Service):
    return execute(service.cancel, order_id, data)


@router.get("/{order_id}/history", response_model=list[OrderEventRead])
def order_history(
    order_id: OrderId,
    service: Service,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return execute(service.history, order_id, offset, limit)
