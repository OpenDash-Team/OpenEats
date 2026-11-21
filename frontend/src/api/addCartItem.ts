import { request } from "./request";

export async function addCartItem(menuItemId: string, quantity: number): Promise<Cart> {
    return request<Cart>("/cart/items", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ menuItemId, quantity }),
    });
}
