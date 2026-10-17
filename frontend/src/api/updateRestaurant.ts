import { request } from "./request";

type RestaurantUpdate = Partial<Pick<Restaurant, "name" | "description" | "address" | "telephone" | "openingHours">>;

export async function updateRestaurant(restaurantId: string, changes: RestaurantUpdate): Promise<Restaurant> {
    return request<Restaurant>(`/restaurants/${encodeURIComponent(restaurantId)}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(changes),
    });
}
