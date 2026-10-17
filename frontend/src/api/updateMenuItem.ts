import { request } from "./request";

type MenuItemUpdate = Partial<Pick<MenuItem, "name" | "description" | "suitableForDiet" | "offers">>;

export async function updateMenuItem(restaurantId: string, menuItemId: string, changes: MenuItemUpdate): Promise<MenuItem> {
    return request<MenuItem>(`/restaurants/${encodeURIComponent(restaurantId)}/menu-items/${encodeURIComponent(menuItemId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(changes),
    });
}
