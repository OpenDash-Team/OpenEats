import { Badge, Card } from 'react-bootstrap'

interface OrderCardProps {
    restaurant: string;
    date: string;
    status: string;
    items: string[];
    total: number;
}

const OrderCard = (props: OrderCardProps) => {
    return (
        <Card>
            <Card.Body>
                <div className="d-flex justify-content-between gap-3 mb-3">
                    <div>
                        <Card.Title className="fs-6 fw-bold">{props.restaurant}</Card.Title>
                        <Card.Text className="fs-8 text-secondary-emphasis">{props.date}</Card.Text>
                    </div>
                    <Badge bg="secondary" className="align-self-start">{props.status}</Badge>
                </div>

                <div className="d-flex justify-content-between gap-3 fs-7">
                    <span className="text-secondary-emphasis">{props.items.join(', ')}</span>
                    <span className="fw-bold">${props.total.toFixed(2)}</span>
                </div>
            </Card.Body>
        </Card>
    )
}

export default OrderCard
