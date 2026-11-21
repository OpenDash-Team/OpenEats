import { request } from "./request";

export async function fetchOrders(): Promise<Order[]> {
    return request<Order[]>("/orders/me");
}
