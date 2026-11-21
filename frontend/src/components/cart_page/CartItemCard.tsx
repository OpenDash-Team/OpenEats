import { Button, Card } from 'react-bootstrap'

interface CartItemCardProps {
    name: string;
    description: string;
    price: number;
    quantity: number;
    onDecrease: () => void;
    onIncrease: () => void;
    onRemove: () => void;
}

const CartItemCard = (props: CartItemCardProps) => {
    return (
        <Card>
            <Card.Body>
                <div className="d-flex justify-content-between gap-3 mb-3">
                    <div>
                        <Card.Title className="fs-6 fw-bold">{props.name}</Card.Title>
                        <Card.Text className="fs-8 text-secondary-emphasis">{props.description}</Card.Text>
                    </div>
                    <span className="fs-7 fw-bold">${(props.price * props.quantity).toFixed(2)}</span>
                </div>
                <div className="d-flex align-items-center">
                    <div className="d-flex align-items-center gap-3 border border-secondary border-2 rounded-5">
                        <Button variant="transparent" size="sm" aria-label={`Decrease ${props.name} quantity`} onClick={props.onDecrease}>−</Button>
                        <span className="fs-7">{props.quantity}</span>
                        <Button variant="transparent" size="sm" aria-label={`Increase ${props.name} quantity`} onClick={props.onIncrease}>+</Button>
                    </div>
                    <Button variant="link" className="fs-7 text-danger ms-auto" onClick={props.onRemove}>Remove</Button>
                </div>
            </Card.Body>
        </Card>
    )
}

export default CartItemCard
