from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

import pytest

from backend.app.core.exceptions import CustomerDeactivatedError, CustomerNotFoundError, DuplicateEmailError
from backend.app.core.security import verify_password
from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import Customer
from backend.app.schemas.customer_request import CustomerCreate, CustomerUpdate
from backend.app.services.customer_service import CustomerService


def make_service(*customers):
    # MagicMock (not Mock) so `with repository.lock():` works
    repository = MagicMock(spec=CustomerRepository)
    repository.get_all_customers.return_value = list(customers)
    return CustomerService(repository), repository


def existing(**changes):
    data = {"id": "c1", "name": "Alex", "email": "alex@example.com", "hashedPassword": "hash"}
    return Customer(**{**data, **changes})


# register

def test_register_saves_customer_with_hashed_password():
    service, repository = make_service()

    customer = service.register_customer(CustomerCreate(name="Jordan", email="jordan@example.com", password="password123"))

    assert customer.hashedPassword != "password123"
    assert verify_password("password123", customer.hashedPassword)
    assert customer.role == "customer"
    assert customer.isActive is True
    repository.save_customers.assert_called_once_with([customer])


def test_register_rejects_email_already_used_with_different_case():
    service, repository = make_service(existing())

    with pytest.raises(DuplicateEmailError):
        service.register_customer(CustomerCreate(name="Other", email="ALEX@example.com", password="password123"))

    repository.save_customers.assert_not_called()


def test_register_rejects_email_of_deactivated_account():
    service, _ = make_service(existing(isActive=False))

    with pytest.raises(DuplicateEmailError):
        service.register_customer(CustomerCreate(name="Other", email="alex@example.com", password="password123"))


# get

def test_get_customer_raises_when_id_is_unknown():
    service, _ = make_service()

    with pytest.raises(CustomerNotFoundError):
        service.get_active_customer("missing")


def test_get_active_customer_raises_for_deactivated_account():
    service, _ = make_service(existing(isActive=False))

    with pytest.raises(CustomerDeactivatedError):
        service.get_active_customer("c1")


# update

def test_update_changes_only_sent_fields():
    service, repository = make_service(existing(telephone="+1-250-555-0100"))

    customer = service.update_customer("c1", CustomerUpdate(address="3333 University Way, Kelowna, BC"))

    assert customer.address == "3333 University Way, Kelowna, BC"
    assert customer.telephone == "+1-250-555-0100"
    assert customer.name == "Alex"
    repository.save_customers.assert_called_once()


def test_update_rejects_email_used_by_another_customer():
    service, repository = make_service(existing(), existing(id="c2", email="taken@example.com"))

    with pytest.raises(DuplicateEmailError):
        service.update_customer("c1", CustomerUpdate(email="taken@example.com"))

    repository.save_customers.assert_not_called()


def test_update_allows_keeping_own_email():
    service, _ = make_service(existing())

    customer = service.update_customer("c1", CustomerUpdate(email="alex@example.com", name="Alex M"))

    assert customer.name == "Alex M"


def test_update_rejects_deactivated_customer():
    service, repository = make_service(existing(isActive=False))

    with pytest.raises(CustomerDeactivatedError):
        service.update_customer("c1", CustomerUpdate(name="New"))

    repository.save_customers.assert_not_called()


# deactivate

def test_deactivate_marks_customer_inactive_and_keeps_them_saved():
    customer = existing()
    service, repository = make_service(customer)

    service.deactivate_customer("c1")

    assert customer.isActive is False
    repository.save_customers.assert_called_once_with([customer])


def test_deactivate_unknown_customer_raises():
    service, _ = make_service()

    with pytest.raises(CustomerNotFoundError):
        service.deactivate_customer("missing")


# Regression: parallel sign-ups used to overwrite each other (found in review)

def register_in_parallel(file_path, emails):
    file_path.write_text("[]")

    def register(email):
        # A new service + repository per call, like separate requests
        service = CustomerService(CustomerRepository(file_path))
        try:
            service.register_customer(CustomerCreate(name="Parallel", email=email, password="password123"))
            return "ok"
        except DuplicateEmailError:
            return "duplicate"

    # map() re-raises any other error from a thread, so a failure shows the real cause
    with ThreadPoolExecutor(max_workers=len(emails)) as executor:
        results = list(executor.map(register, emails))

    return results, CustomerRepository(file_path).get_all_customers()


def test_parallel_registrations_are_all_saved(tmp_path):
    results, saved = register_in_parallel(tmp_path / "customers.json", [f"user{n}@example.com" for n in range(8)])

    assert results.count("ok") == 8
    assert len(saved) == 8


def test_parallel_registrations_with_same_email_create_only_one_account(tmp_path):
    results, saved = register_in_parallel(tmp_path / "customers.json", ["same@example.com"] * 4)

    assert results.count("ok") == 1
    assert results.count("duplicate") == 3
    assert len(saved) == 1
