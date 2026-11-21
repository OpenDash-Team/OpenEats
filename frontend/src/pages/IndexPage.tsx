import { Navigate } from "react-router-dom"
import CreateRestaurantPage from "./CreateRestaurantPage"
import DiscoverPage from "./DiscoverPage"
import RestaurantManagementPage from "./RestaurantManagementPage"
import RestaurantSelectPage from "./RestaurantSelectPage"

const IndexPage = () => {
    const userMode = localStorage.getItem("userMode") ?? ""
    const restaurantId = localStorage.getItem("restaurantId") ?? ""

    if (userMode === "restaurant") {
        if (!restaurantId) {
            return <RestaurantSelectPage />
        }
        else if (restaurantId === "new") {
            return <CreateRestaurantPage />
        }
        else {
            return <RestaurantManagementPage restaurantId={restaurantId} />
        }
    } 

    else if (userMode === "customer") {
        return <DiscoverPage />
    }

    else {
        return <Navigate to="/login" replace />
    }
}

export default IndexPage