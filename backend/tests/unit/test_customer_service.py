from unittest.mock import Mock

import pytest

from src.models import Customer
from src.repositories.customers import CustomerRepository
from src.services.customers import CustomerHasOrders, CustomerNotFound, CustomerService


def test_missing_customer_stops_delete():
    repository = Mock(spec=CustomerRepository)
    repository.get.return_value = None
    service = CustomerService(repository)
    with pytest.raises(CustomerNotFound):
        service.delete(1)
    repository.has_orders.assert_not_called()
    repository.delete.assert_not_called()


def test_linked_customer_is_preserved():
    repository = Mock(spec=CustomerRepository)
    repository.get.return_value = Customer(id=1, name="Ana", phone="35999998888")
    repository.has_orders.return_value = True
    service = CustomerService(repository)
    with pytest.raises(CustomerHasOrders):
        service.delete(1)
    repository.delete.assert_not_called()
