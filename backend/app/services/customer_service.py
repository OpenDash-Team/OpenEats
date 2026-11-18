from ..core.exceptions import CustomerDeactivatedError, CustomerNotFoundError, DuplicateEmailError
from ..core.security import hash_password
from ..repositories.customer_repository import CustomerRepository
from ..schemas.customer import Customer
from ..schemas.customer_request import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, repository: CustomerRepository):
        self.repository: CustomerRepository = repository

    def register_customer(self, request: CustomerCreate) -> Customer:
        # The plain password is never stored, only its hash. Hashing is slow, so it's done
        # before taking the lock to keep other requests from waiting on it.
        data = request.model_dump(exclude={"password"})
        new_customer = Customer(**data, hashedPassword=hash_password(request.password))

        with self.repository.lock():
            customers = self.repository.get_all_customers()
            self._check_email_not_taken(customers, request.email)

            customers.append(new_customer)
            self.repository.save_customers(customers)

        return new_customer

    def get_customer_by_email(self, email: str) -> Customer | None:
        return self.repository.get_customer_by_email(email)

    def get_active_customer(self, customer_id: str) -> Customer:
        return self._find_active(self.repository.get_all_customers(), customer_id)

    def update_customer(self, customer_id: str, request: CustomerUpdate) -> Customer:
        # Fields that were not sent (or sent as null) keep their current value
        changes = request.model_dump(exclude_none=True)

        with self.repository.lock():
            customers = self.repository.get_all_customers()
            customer = self._find_active(customers, customer_id)

            if "email" in changes:
                other_customers = [c for c in customers if c.id != customer_id]
                self._check_email_not_taken(other_customers, changes["email"])

            for field, value in changes.items():
                setattr(customer, field, value)

            self.repository.save_customers(customers)

        return customer

    def deactivate_customer(self, customer_id: str) -> None:
        # Soft delete: the account stays in the file so past orders still point to a real customer,
        # but it can't sign in or be used anymore.
        with self.repository.lock():
            customers = self.repository.get_all_customers()
            customer = self._find_active(customers, customer_id)

            customer.isActive = False
            self.repository.save_customers(customers)

    def _find_active(self, customers: list[Customer], customer_id: str) -> Customer:
        customer = next((c for c in customers if c.id == customer_id), None)
        if customer is None:
            raise CustomerNotFoundError(f"Customer with id '{customer_id}' is not found")
        if not customer.isActive:
            raise CustomerDeactivatedError(f"Customer with id '{customer_id}' is deactivated")
        return customer

    def _check_email_not_taken(self, customers: list[Customer], email: str) -> None:
        # Deactivated accounts still hold their email, so it can't be reused for a new account
        if any(customer.email == email.lower() for customer in customers):
            raise DuplicateEmailError(f"A customer with email '{email}' already exists")
