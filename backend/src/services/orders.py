from sqlalchemy.exc import IntegrityError

from src.models.enums import OrderStatus
from src.repositories.orders import OrderRepository
from src.schemas.orders import OrderCreate, OrderPatch


class OrderNotFound(Exception):
    pass


class OrderCustomerNotFound(Exception):
    pass


class OrderConflict(Exception):
    pass


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    def get(self, order_id: int, *, lock: bool = False):
        order = self.repository.get(order_id, lock=lock)
        if order is None:
            raise OrderNotFound
        return order

    def list(self, offset: int = 0, limit: int = 20):
        return self.repository.list(offset, limit)

    def _check_customer(self, customer_id: int):
        if not self.repository.customer_exists(customer_id):
            raise OrderCustomerNotFound

    def _rollback_integrity_error(self, exc: IntegrityError):
        self.repository.session.rollback()
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        if (
            getattr(exc.orig, "sqlstate", None) == "23503"
            and constraint == "fk_service_orders_customer_id_customers"
        ):
            raise OrderCustomerNotFound from exc
        raise exc

    def create(self, data: OrderCreate):
        self._check_customer(data.customer_id)
        try:
            order = self.repository.create(data)
            self.repository.session.commit()
            return order
        except IntegrityError as exc:
            self._rollback_integrity_error(exc)

    def update(self, order_id: int, data: OrderCreate | OrderPatch):
        order = self.get(order_id, lock=True)
        if order.status != OrderStatus.RECEIVED:
            raise OrderConflict(
                "Somente ordens recebidas permitem editar os dados de abertura."
            )
        values = data.model_dump(exclude_unset=isinstance(data, OrderPatch))
        if "customer_id" in values:
            self._check_customer(values["customer_id"])
        try:
            updated = self.repository.update(order, values)
            self.repository.session.commit()
            return updated
        except IntegrityError as exc:
            self._rollback_integrity_error(exc)

    def delete(self, order_id: int):
        order = self.get(order_id, lock=True)
        if (
            order.status != OrderStatus.RECEIVED
            or not self.repository.has_only_open_event(order_id)
        ):
            raise OrderConflict("Não é possível excluir uma ordem com andamento.")
        self.repository.delete(order)
        self.repository.session.commit()
