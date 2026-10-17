import { request } from "./request";

type RestaurantCreate = Pick<Restaurant, "name" | "address" | "telephone" | "openingHours"> &
    Partial<Pick<Restaurant, "description">>;

export async function createRestaurant(data: RestaurantCreate): Promise<Restaurant> {
    return request<Restaurant>("/restaurants", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
}
