import { Badge, Card } from "react-bootstrap"

interface MenuItemCardProps {
    title: string;
    description: string;
    price: number;
    currency: string;
    availability: ItemAvailability;
}

const MenuItemCard = (props: MenuItemCardProps) => {
    return (
        <Card className="clickable-card">
            <Card.Body>
                <Card.Title className="fs-6 fw-bold d-flex flex-row align-items-center gap-2">{props.title} <Badge bg="secondary">{props.currency} {props.price.toFixed(2)}</Badge></Card.Title>
                <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
                {props.availability === "https://schema.org/OutOfStock" && <Card.Text className="fs-8 text-secondary">Out of stock</Card.Text>}
            </Card.Body>
        </Card>
    )
}

export default MenuItemCard
