import { Button, Card } from 'react-bootstrap'

interface CartItemCardProps {
    name: string;
    lineTotal: string;
    currency: string | null;
    quantity: number;
    available: boolean;
    busy: boolean;
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
                        { !props.available && <Card.Text className="fs-8 text-secondary-emphasis">Unavailable</Card.Text> }
                    </div>
                    <span className="fs-7 fw-bold">{props.lineTotal} {props.currency}</span>
                </div>
                <div className="d-flex align-items-center">
                    <div className="d-flex align-items-center gap-3 border border-secondary border-2 rounded-5">
                        <Button variant="transparent" size="sm" aria-label={`Decrease ${props.name} quantity`} disabled={props.busy} onClick={props.onDecrease}>−</Button>
                        <span className="fs-7">{props.quantity}</span>
                        <Button variant="transparent" size="sm" aria-label={`Increase ${props.name} quantity`} disabled={props.busy || !props.available} onClick={props.onIncrease}>+</Button>
                    </div>
                    <Button variant="link" className="fs-7 text-danger ms-auto" disabled={props.busy} onClick={props.onRemove}>Remove</Button>
                </div>
            </Card.Body>
        </Card>
    )
}

export default CartItemCard
