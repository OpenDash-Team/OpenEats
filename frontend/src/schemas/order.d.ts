interface Order {
    id: string;
    customerId: string;
    restaurantId: string;
    cartId: string;
    items: OrderItem[];
    currency: string;
    subtotal: string;
    total: string;
    deliveryAddress: string;
    createdAt: string;
    status: "created";
}
