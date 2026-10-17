import { Button, Container } from "react-bootstrap"
import RestaurantCard from "../components/discover_page/RestaurantCard"
import NewRestaurantCard from "../components/restaurant_select_page/NewRestaurantCard";
import { useEffect, useState } from "react";
import { fetchRestaurants } from "../api/fetchRestaurants";

const RestaurantSelectPage = () => {
    const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchRestaurants().then(setRestaurants).catch((cause) => setError(cause instanceof Error ? cause.message : "Could not load restaurants"));
    }, []);
    const backToViewSelector = () => {
        localStorage.setItem("userMode", "");
        window.location.replace('/')
    }

    const newRestaurant = () => {
        localStorage.setItem("restaurantId", "new");
        window.location.replace("/")
    }

    const selectRestaurant = (restaurantId: string) => {
        localStorage.setItem("restaurantId", restaurantId);
        window.location.replace("/")
    }

    return (
        <div data-bs-theme="dark" className="min-vh-100 bg-dark text-white py-4 d-flex flex-column" style={{paddingInline: "8rem"}}>
            <Container className="d-flex flex-column align-items-center gap-4 mt-4">
                <Button variant="outline-secondary" className="fs-7 align-self-start mb-2" onClick = {backToViewSelector}>
                    Back to View Selector
                </Button>

                <Container>
                    <h2>Select Your Restaurant</h2>
                    <p className="text-secondary-emphasis">{restaurants.length} restaurants available</p>
                </Container>

                <Container className="d-flex flex-wrap gap-4 card-grid">
                    <NewRestaurantCard onClick={() => { newRestaurant() }} />
                    {restaurants.map((restaurant) => <RestaurantCard key={restaurant.id} title={restaurant.name} description={restaurant.description} onClick={() => selectRestaurant(restaurant.id)} />)}
                </Container>
                {error && <p role="alert" className="text-danger">{error}</p>}
            </Container>
        </div>
    )
}

export default RestaurantSelectPage
