class RestaurantNotFoundError(Exception):
    """No restaurant has the given ID."""

class DuplicateRestaurantError(Exception):
    """Another restaurant already has the same name and address."""

class CustomerNotFoundError(Exception):
    """No customer has the given ID."""

class DuplicateEmailError(Exception):
    """Another customer is already registered with this email."""

class CustomerDeactivatedError(Exception):
    """The customer's account has been deactivated."""
