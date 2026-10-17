import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Button, Container } from "react-bootstrap";
import UserPageLayout from "../components/shared/UserPageLayout";
import MenuItemCard from "../components/restaurant_page/MenuItemCard";
import MenuSection from "../components/restaurant_page/MenuSection";
import { fetchRestaurantDetails } from "../api/fetchRestaurantDetails";

const asArray = <T,>(value: T | T[] | null | undefined): T[] =>
    value == null ? [] : Array.isArray(value) ? value : [value];

const renderSection = (section: MenuSection) => (
    <MenuSection key={section.id} title={section.name}>
        {asArray(section.hasMenuItem).map((item) => {
            const offer = asArray(item.offers)[0];
            return <MenuItemCard key={item.id} title={item.name} description={item.description} price={Number(offer.price)} currency={offer.priceCurrency} availability={offer.availability} />;
        })}
        {asArray(section.hasMenuSection).map(renderSection)}
    </MenuSection>
);

const RestaurantPage = () => {
    const { restaurantId } = useParams();
    const navigate = useNavigate();
    const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        if (!restaurantId) return;
        fetchRestaurantDetails(restaurantId).then(setRestaurant).catch((cause) => setError(cause instanceof Error ? cause.message : "Could not load restaurant"));
    }, [restaurantId]);

    return (
        <UserPageLayout>
            <Button variant="outline-secondary" className="fs-7 align-self-start mb-5" onClick={() => navigate("/")}>Back to Discover</Button>
            {error && <p role="alert" className="text-danger">{error}</p>}
            {!restaurant && !error && <p>Loading...</p>}
            {restaurant && <>
                <h3>{restaurant.name}</h3>
                {restaurant.description && <p className="text-secondary-emphasis">{restaurant.description}</p>}
                <hr className="mt-2 mb-5" />
                <Container className="d-flex flex-wrap gap-5 card-grid">
                    {asArray(restaurant.hasMenu?.hasMenuSection).map(renderSection)}
                    {!restaurant.hasMenu && <p className="text-secondary">No menu available yet.</p>}
                </Container>
            </>}
        </UserPageLayout>
    );
};

export default RestaurantPage;
