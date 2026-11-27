from sqlalchemy.exc import IntegrityError

from src.models import Customer
from src.repositories.customers import CustomerRepository
from src.schemas.customers import CustomerCreate, CustomerPatch


class CustomerNotFound(Exception):
    pass


class CustomerHasOrders(Exception):
    pass


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository = repository

    def get(self, customer_id: int) -> Customer:
        customer = self.repository.get(customer_id)
        if customer is None:
            raise CustomerNotFound
        return customer

    def list(self, query: str | None = None, offset: int = 0, limit: int = 20):
        return self.repository.list(query.strip() if query else None, offset, limit)

    def create(self, data: CustomerCreate) -> Customer:
        customer = self.repository.create(data)
        self.repository.session.commit()
        return customer

    def update(
        self, customer_id: int, data: CustomerCreate | CustomerPatch
    ) -> Customer:
        customer = self.get(customer_id)
        values = data.model_dump(exclude_unset=isinstance(data, CustomerPatch))
        updated = self.repository.update(customer, values)
        self.repository.session.commit()
        return updated

    def delete(self, customer_id: int) -> None:
        customer = self.get(customer_id)
        if self.repository.has_orders(customer_id):
            raise CustomerHasOrders
        try:
            self.repository.delete(customer)
            self.repository.session.commit()
        except IntegrityError as exc:
            self.repository.session.rollback()
            # A FK protege inclusive contra vinculos criados apos a consulta acima.
            constraint = getattr(
                getattr(exc.orig, "diag", None), "constraint_name", None
            )
            if (
                getattr(exc.orig, "sqlstate", None) == "23503"
                and constraint == "fk_service_orders_customer_id_customers"
            ):
                raise CustomerHasOrders from exc
            raise
