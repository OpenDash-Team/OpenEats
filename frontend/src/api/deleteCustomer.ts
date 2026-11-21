import { request } from "./request";

export async function deleteCustomer(): Promise<void> {
    return request<void>("/customers/me", { method: "DELETE" });
}
