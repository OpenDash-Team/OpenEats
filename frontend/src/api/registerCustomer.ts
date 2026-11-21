import { request } from "./request";

type CustomerCreate = Pick<Customer, "name" | "email"> &
    Partial<Pick<Customer, "telephone" | "address">> & { password: string };

export async function registerCustomer(data: CustomerCreate): Promise<Customer> {
    const customer = {
        ...data,
        telephone: data.telephone?.trim() || undefined,
        address: data.address?.trim() || undefined,
    };

    return request<Customer>("/customers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(customer),
    });
}
