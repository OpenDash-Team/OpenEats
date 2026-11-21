import { Button, Card } from 'react-bootstrap'

interface CartSummaryProps {
    total: number;
    onCheckout?: () => void;
}

const CartSummary = (props: CartSummaryProps) => {
    return (
        <Card>
            <Card.Body>
                <Card.Title className="fs-6 fw-bold">Order Summary</Card.Title>
                <hr />
                <div className="d-flex justify-content-between fs-7 mb-3">
                    <span>Total</span>
                    <span className="fw-bold">${props.total.toFixed(2)}</span>
                </div>
                <Button variant="primary" className="w-100 fs-7" onClick={props.onCheckout}>Checkout</Button>
            </Card.Body>
        </Card>
    )
}

export default CartSummary
