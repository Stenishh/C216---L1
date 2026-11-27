from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.repositories.customers import CustomerRepository
from src.schemas.customers import CustomerCreate, CustomerPatch, CustomerRead
from src.services.customers import CustomerHasOrders, CustomerNotFound, CustomerService

router = APIRouter(prefix="/customers", tags=["Clientes"])
CustomerId = Annotated[int, Path(gt=0)]


def get_customer_service(
    session: Annotated[Session, Depends(get_db)],
) -> CustomerService:
    return CustomerService(CustomerRepository(session))


Service = Annotated[CustomerService, Depends(get_customer_service)]


def customer_not_found() -> HTTPException:
    return HTTPException(status_code=404, detail="Cliente não encontrado.")


@router.post("/", response_model=CustomerRead, status_code=201)
def create_customer(data: CustomerCreate, service: Service, response: Response):
    customer = service.create(data)
    response.headers["Location"] = f"/customers/{customer.id}"
    return customer


@router.get("/", response_model=list[CustomerRead])
def list_customers(
    service: Service,
    q: Annotated[str | None, Query(max_length=100)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    return service.list(q, offset, limit)


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(customer_id: CustomerId, service: Service):
    try:
        return service.get(customer_id)
    except CustomerNotFound as exc:
        raise customer_not_found() from exc


@router.put("/{customer_id}", response_model=CustomerRead)
def replace_customer(customer_id: CustomerId, data: CustomerCreate, service: Service):
    try:
        return service.update(customer_id, data)
    except CustomerNotFound as exc:
        raise customer_not_found() from exc


@router.patch("/{customer_id}", response_model=CustomerRead)
def patch_customer(customer_id: CustomerId, data: CustomerPatch, service: Service):
    try:
        return service.update(customer_id, data)
    except CustomerNotFound as exc:
        raise customer_not_found() from exc


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: CustomerId, service: Service):
    try:
        service.delete(customer_id)
    except CustomerNotFound as exc:
        raise customer_not_found() from exc
    except CustomerHasOrders as exc:
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir um cliente com ordens em andamento vinculadas.",
        ) from exc
    return Response(status_code=204)
