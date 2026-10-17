import { request } from "./request";

export async function deleteMenuItem(restaurantId: string, menuItemId: string): Promise<void> {
    return request<void>(`/restaurants/${encodeURIComponent(restaurantId)}/menu-items/${encodeURIComponent(menuItemId)}`, {
        method: "DELETE",
    });
}
