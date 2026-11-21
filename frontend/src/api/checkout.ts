import { request } from "./request";

export async function checkout(): Promise<Order> {
    return request<Order>("/checkout", { method: "POST" });
}
