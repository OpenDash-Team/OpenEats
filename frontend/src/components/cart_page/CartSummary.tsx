import { Button, Card } from 'react-bootstrap'

interface CartSummaryProps {
    subtotal: string;
    total: string;
    currency: string | null;
    disabled: boolean;
    onCheckout: () => void;
}

const CartSummary = (props: CartSummaryProps) => {
    return (
        <Card>
            <Card.Body>
                <Card.Title className="fs-6 fw-bold">Order Summary</Card.Title>
                <hr />
                <div className="d-flex justify-content-between fs-7 mb-3">
                    <span>Subtotal</span>
                    <span>{props.subtotal} {props.currency}</span>
                </div>
                <div className="d-flex justify-content-between fs-7 mb-3">
                    <span>Total</span>
                    <span className="fw-bold">{props.total} {props.currency}</span>
                </div>
                <Button variant="primary" className="w-100 fs-7" disabled={props.disabled} onClick={props.onCheckout}>Checkout</Button>
            </Card.Body>
        </Card>
    )
}

export default CartSummary
