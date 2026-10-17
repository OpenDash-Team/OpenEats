import { request } from "./request";

export async function fetchRestaurantDetails(restaurantId: string): Promise<Restaurant> {
    return request<Restaurant>(`/restaurants/${encodeURIComponent(restaurantId)}`);
}
