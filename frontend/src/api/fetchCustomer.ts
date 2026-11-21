import { request } from "./request";

export async function fetchCustomer(): Promise<Customer> {
    return request<Customer>("/customers/me");
}
