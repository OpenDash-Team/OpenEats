import { useState } from "react"
import { Badge, Button, Card } from "react-bootstrap"

interface MenuItemCardProps {
    title: string;
    description: string;
    price: number;
    currency: string;
    availability: ItemAvailability;
    onAddToCart: (quantity: number) => Promise<void>;
}

const MenuItemCard = (props: MenuItemCardProps) => {
    const [quantity, setQuantity] = useState(1);
    const [adding, setAdding] = useState(false);
    const [error, setError] = useState('');
    const [added, setAdded] = useState(false);

    const addToCart = async () => {
        setAdding(true);
        setError('');
        setAdded(false);

        try {
            await props.onAddToCart(quantity);
            setQuantity(1);
            setAdded(true);
        } catch (cause) {
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not add item to cart.');
        } finally {
            setAdding(false);
        }
    }

    return (
        <Card className="clickable-card">
            <Card.Body className="d-flex flex-row justify-content-between align-items-center gap-5">
                <div>
                    <Card.Title className="fs-6 fw-bold d-flex flex-row align-items-center gap-2">{props.title} <Badge bg="secondary">{props.currency} {props.price.toFixed(2)}</Badge></Card.Title>
                    <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
                    {added && <p role="status" className="fs-8 text-success mt-2 mb-0">Added to cart.</p>}
                </div>
                <div className="flex-shrink-0">
                    {props.availability === "https://schema.org/OutOfStock" && <Card.Text className="fs-8 text-secondary">Out of stock</Card.Text>}
                    {props.availability !== "https://schema.org/OutOfStock" &&
                        <div className="d-flex align-items-center gap-3">
                            <div className="d-flex align-items-center gap-3 border border-secondary border-2 rounded-5">
                                <Button variant="transparent" size="sm" aria-label={`Decrease ${props.title} quantity`} onClick={() => { if (!adding) setQuantity(Math.max(1, quantity - 1)); }}>−</Button>
                                <span className="fs-7">{quantity}</span>
                                <Button variant="transparent" size="sm" aria-label={`Increase ${props.title} quantity`} onClick={() => { if (!adding) setQuantity(Math.min(99, quantity + 1)); }}>+</Button>
                            </div>
                            <Button variant="primary" className="fs-7 rounded-5" disabled={adding} onClick={addToCart}>{adding ? "Adding..." : "Add to Cart"}</Button>
                        </div>
                    }
                    {error && <p role="alert" className="fs-8 text-danger mt-2 mb-0">{error}</p>}
                </div>
            </Card.Body>
        </Card>
    )
}

export default MenuItemCard
