import { request } from "./request";

interface RestaurantFilters {
    name?: string;
    hasMenu?: boolean;
    sort_by?: string;
    sort_desc?: boolean;
}

export async function fetchRestaurants(filters: RestaurantFilters = {}): Promise<Restaurant[]> {
    const query = new URLSearchParams();
    for (const [key, value] of Object.entries(filters)) {
        if (value !== undefined) query.set(key, String(value));
    }
    const search = query.size ? `?${query}` : "";
    return request<Restaurant[]>(`/restaurants${search}`);
}
