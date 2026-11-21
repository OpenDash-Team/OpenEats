import { request } from "./request";

export async function removeCartItem(menuItemId: string): Promise<Cart> {
    return request<Cart>(`/cart/items/${encodeURIComponent(menuItemId)}`, { method: "DELETE" });
}
