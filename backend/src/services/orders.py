from sqlalchemy.exc import IntegrityError

from src.models.enums import BudgetDecision, EventAction, OrderStatus
from src.repositories.orders import OrderRepository
from src.schemas.orders import BudgetRejection, DiagnosisPatch, OrderCreate, OrderPatch


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

    def _require_status(self, order_id: int, status: OrderStatus):
        order = self.get(order_id, lock=True)
        if order.status != status:
            raise OrderConflict("Ação não permitida no status atual da ordem.")
        return order

    def _record_action(self, order, action, previous_status, **event_values):
        try:
            self.repository.add_event(order, action, previous_status, **event_values)
            self.repository.session.commit()
            return order
        except Exception:
            self.repository.session.rollback()
            raise

    def begin_diagnosis(self, order_id: int):
        order = self._require_status(order_id, OrderStatus.RECEIVED)
        order.status = OrderStatus.IN_DIAGNOSIS
        return self._record_action(
            order, EventAction.BEGIN_DIAGNOSIS, OrderStatus.RECEIVED
        )

    def update_diagnosis(self, order_id: int, data: DiagnosisPatch):
        order = self._require_status(order_id, OrderStatus.IN_DIAGNOSIS)
        try:
            updated = self.repository.update(order, data.model_dump(exclude_unset=True))
            self.repository.session.commit()
            return updated
        except Exception:
            self.repository.session.rollback()
            raise

    def request_approval(self, order_id: int):
        order = self._require_status(order_id, OrderStatus.IN_DIAGNOSIS)
        if (
            not order.diagnosis
            or not order.diagnosis.strip()
            or order.budget_amount is None
        ):
            raise OrderConflict(
                "Informe diagnóstico e valor do orçamento antes de solicitar aprovação."
            )
        order.status = OrderStatus.AWAITING_APPROVAL
        order.budget_decision = BudgetDecision.PENDING
        return self._record_action(
            order, EventAction.REQUEST_APPROVAL, OrderStatus.IN_DIAGNOSIS
        )

    def _pending_budget(self, order_id: int):
        order = self._require_status(order_id, OrderStatus.AWAITING_APPROVAL)
        if order.budget_decision != BudgetDecision.PENDING:
            raise OrderConflict("O orçamento não está pendente de decisão.")
        return order

    def approve_budget(self, order_id: int):
        order = self._pending_budget(order_id)
        order.budget_decision = BudgetDecision.APPROVED
        return self._record_action(
            order,
            EventAction.APPROVE_BUDGET,
            OrderStatus.AWAITING_APPROVAL,
            approved_amount=order.budget_amount,
        )

    def reject_budget(self, order_id: int, data: BudgetRejection):
        order = self._pending_budget(order_id)
        order.budget_decision = BudgetDecision.REJECTED
        order.cancellation_reason = data.reason
        order.status = OrderStatus.CANCELLED
        return self._record_action(
            order,
            EventAction.REJECT_BUDGET,
            OrderStatus.AWAITING_APPROVAL,
            observation=data.reason,
        )

    def start_repair(self, order_id: int):
        order = self._require_status(order_id, OrderStatus.AWAITING_APPROVAL)
        if order.budget_decision != BudgetDecision.APPROVED:
            raise OrderConflict("O reparo exige orçamento aprovado.")
        order.status = OrderStatus.IN_REPAIR
        return self._record_action(
            order, EventAction.START_REPAIR, OrderStatus.AWAITING_APPROVAL
        )
