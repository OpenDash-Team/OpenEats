class RestaurantNotFoundError(Exception):
    """No restaurant has the given ID."""

class DuplicateRestaurantError(Exception):
    """Another restaurant already has the same name and address."""
