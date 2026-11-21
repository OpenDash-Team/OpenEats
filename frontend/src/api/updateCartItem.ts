import { request } from "./request";

export async function updateCartItem(menuItemId: string, quantity: number): Promise<Cart> {
    return request<Cart>(`/cart/items/${encodeURIComponent(menuItemId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity }),
    });
}
