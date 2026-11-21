interface Cart {
    id: string;
    customerId: string;
    restaurantId: string | null;
    items: CartItem[];
    currency: string | null;
    subtotal: string;
    total: string;
}
