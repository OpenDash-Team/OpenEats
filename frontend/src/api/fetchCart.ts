import { request } from "./request";

export async function fetchCart(): Promise<Cart> {
    return request<Cart>("/cart");
}
