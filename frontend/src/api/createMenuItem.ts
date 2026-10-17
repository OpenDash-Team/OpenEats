import { request } from "./request";

type MenuItemCreate = Pick<MenuItem, "name" | "suitableForDiet" | "offers"> &
    Partial<Pick<MenuItem, "description">>;

export async function createMenuItem(restaurantId: string, data: MenuItemCreate): Promise<MenuItem> {
    return request<MenuItem>(`/restaurants/${encodeURIComponent(restaurantId)}/menu-items`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
}
