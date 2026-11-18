from pathlib import Path

from backend.app.repositories.customer_repository import CustomerRepository
from backend.app.schemas.customer import Customer


def make_repository(tmp_path):
    repository = CustomerRepository(tmp_path / "customers.json")
    repository.save_customers([
        Customer(id="c1", name="Alex", email="alex@example.com", hashedPassword="hash"),
        Customer(id="c2", name="Sam", email="sam@example.com", hashedPassword="hash"),
    ])
    return repository


def test_get_customer_by_id(tmp_path):
    repository = make_repository(tmp_path)

    assert repository.get_customer_by_id("c2").name == "Sam"
    assert repository.get_customer_by_id("missing") is None


def test_get_customer_by_email_ignores_case(tmp_path):
    repository = make_repository(tmp_path)

    assert repository.get_customer_by_email("ALEX@Example.com").id == "c1"
    assert repository.get_customer_by_email("nobody@example.com") is None


def test_ids_stay_the_same_after_reloading(tmp_path):
    repository = make_repository(tmp_path)

    reloaded = CustomerRepository(tmp_path / "customers.json")

    assert [c.id for c in reloaded.get_all_customers()] == ["c1", "c2"]


def test_sample_data_customers_are_valid():
    sample_file = Path(__file__).resolve().parents[1] / "sample-data" / "customers.json"

    roles = [c.role for c in CustomerRepository(sample_file).get_all_customers()]

    assert sorted(roles) == ["customer", "owner"]
