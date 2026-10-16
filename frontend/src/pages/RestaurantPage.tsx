import { useNavigate, useParams } from "react-router-dom"
import { Button, Container } from "react-bootstrap";
import CustomerPageLayout from "../components/shared/CustomerPageLayout";
import MenuItemCard from "../components/restaurant_page/MenuItemCard";
import MenuSection from "../components/restaurant_page/MenuSection";

const RestaurantPage = () => {
    const { restaurantId } = useParams();

    const navigate = useNavigate();

    return  (
        <CustomerPageLayout>
            <Button variant="outline-secondary" className="fs-7 align-self-start mb-5" onClick={() => navigate("/")}>
                Back to Discover
            </Button>

            <h3>Mama Rosa's Pizza</h3>
            
            <hr className="mt-2 mb-5" />

            <Container className="d-flex flex-wrap gap-5 card-grid">
                <MenuSection title="Pizza">
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                </MenuSection>

                <MenuSection title="Pizza">
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                    <MenuItemCard title="Margherita Pizza" description="San Marzano tomatoes, fior di latte, fresh basil, extra-virgin olive oil" price={20.99} />
                </MenuSection>
            </Container>
        </CustomerPageLayout>
    )
}

export default RestaurantPage