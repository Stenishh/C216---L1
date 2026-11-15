from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models import Customer, ServiceOrder
from src.schemas.customers import CustomerCreate


class CustomerRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, customer_id: int) -> Customer | None:
        return self.session.get(Customer, customer_id)

    def list(self, query: str | None, offset: int, limit: int) -> list[Customer]:
        statement = select(Customer).order_by(Customer.id)
        if query:
            statement = statement.where(Customer.name.icontains(query, autoescape=True))
        return list(self.session.scalars(statement.offset(offset).limit(limit)))

    def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        self.session.add(customer)
        self.session.flush()
        return customer

    def update(self, customer: Customer, values: dict) -> Customer:
        for field, value in values.items():
            setattr(customer, field, value)
        self.session.flush()
        return customer

    def has_orders(self, customer_id: int) -> bool:
        statement = (
            select(ServiceOrder.id)
            .where(ServiceOrder.customer_id == customer_id)
            .limit(1)
        )
        return self.session.scalar(statement) is not None

    def delete(self, customer: Customer) -> None:
        self.session.delete(customer)
        self.session.flush()
