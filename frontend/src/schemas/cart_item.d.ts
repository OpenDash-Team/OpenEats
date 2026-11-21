interface CartItem {
    menuItemId: string;
    name: string | null;
    quantity: number;
    unitPrice: string | null;
    lineTotal: string;
    available: boolean;
}
