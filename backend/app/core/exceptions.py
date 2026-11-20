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

class MenuItemNotFoundError(Exception):
    """No restaurant has a menu item with the given ID."""

class MenuItemUnavailableError(Exception):
    """The menu item exists but can't be ordered right now (out of stock)."""

class DifferentRestaurantError(Exception):
    """The cart already has items from another restaurant."""

class CartItemNotFoundError(Exception):
    """The menu item is not in the customer's cart."""

class CartQuantityError(Exception):
    """The change would put a cart item's quantity outside the allowed range."""

class CheckoutError(Exception):
    """Base exception for expected checkout failures."""

class CheckoutValidationError(CheckoutError):
    """The cart or customer does not satisfy checkout requirements."""

class CheckoutPermissionError(CheckoutError):
    """The authenticated account is not allowed to check out."""