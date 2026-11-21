import { request } from "./request";

export async function clearCart(): Promise<Cart> {
    return request<Cart>("/cart", { method: "DELETE" });
}
