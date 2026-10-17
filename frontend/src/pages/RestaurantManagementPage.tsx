import { Tab, Tabs } from "react-bootstrap";
import UserPageLayout from "../components/shared/UserPageLayout";
import { useEffect, useState } from "react";
import GeneralManagement from "../components/restaurant_management_page/GeneralManagement";
import MenuManagement from "../components/restaurant_management_page/MenuManagement";
import { fetchRestaurantDetails } from "../api/fetchRestaurantDetails";

interface RestaurantManagementPageProps {
    restaurantId: string;
}

const RestaurantManagementPage = ({ restaurantId }: RestaurantManagementPageProps) => {
    const [activeTab, setActiveTab] = useState<string>("details")
    const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
    const [error, setError] = useState("");

    useEffect(() => {
        fetchRestaurantDetails(restaurantId).then(setRestaurant).catch((cause) => setError(cause instanceof Error ? cause.message : "Could not load restaurant"));
    }, [restaurantId]);

    return (
        <UserPageLayout className="gap-4 pt-5">
            <p className="fs-4 fw-bold m-0">{restaurant?.name ?? "Restaurant"}</p>
            {error && <p role="alert" className="text-danger">{error}</p>}
            {!restaurant && !error && <p>Loading...</p>}

            {restaurant && <Tabs
                activeKey={activeTab}
                onSelect={(key) => setActiveTab(key!)}
            >
                <Tab eventKey="details" title="Details">
                    <GeneralManagement restaurant={restaurant} onSaved={setRestaurant} />
                </Tab>

                <Tab eventKey="menu" title="Menu">
                    <MenuManagement restaurant={restaurant} onChanged={setRestaurant} />
                </Tab>
            </Tabs>}
        </UserPageLayout>
    );
}

export default RestaurantManagementPage
