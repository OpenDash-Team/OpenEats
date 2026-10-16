import { Badge, Button, Card } from "react-bootstrap"

interface MenuItemCardProps {
    title: string;
    description: string;
    price: number;
}

const MenuItemCard = (props: MenuItemCardProps) => {
    return (
        <Card className="clickable-card">
            <Card.Body>
                <Card.Title className="fs-6 fw-bold d-flex flex-row align-items-center gap-2">{props.title} <Badge bg="secondary">${props.price}</Badge></Card.Title>
                <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
                <Button variant="success" className="fs-8">Add to Cart</Button>
            </Card.Body>
        </Card>
    )
}

export default MenuItemCard