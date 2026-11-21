import { request } from "./request";

type CustomerUpdate = Partial<Pick<Customer, "name" | "email" | "telephone" | "address">>;

export async function updateCustomer(changes: CustomerUpdate): Promise<Customer> {
    return request<Customer>("/customers/me", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(changes),
    });
}
