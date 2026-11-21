import { Badge, Button, Card } from "react-bootstrap"

interface MenuItemCardProps {
    title: string;
    description: string;
    price: number;
    currency: string;
    availability: ItemAvailability;
    onAddToCart?: () => void;
}

const MenuItemCard = (props: MenuItemCardProps) => {
    return (
        <Card className="clickable-card">
            <Card.Body className="d-flex flex-row justify-content-between align-items-center gap-5">
                <div>
                    <Card.Title className="fs-6 fw-bold d-flex flex-row align-items-center gap-2">{props.title} <Badge bg="secondary">{props.currency} {props.price.toFixed(2)}</Badge></Card.Title>
                    <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
                </div>
                <div className="flex-shrink-0">
                    {props.availability === "https://schema.org/OutOfStock" && <Card.Text className="fs-8 text-secondary">Out of stock</Card.Text>}
                    {props.availability !== "https://schema.org/OutOfStock" && <Button variant="primary" className="fs-7 rounded-5" onClick={props.onAddToCart}>Add to Cart</Button>}
                </div>
            </Card.Body>
        </Card>
    )
}

export default MenuItemCard
