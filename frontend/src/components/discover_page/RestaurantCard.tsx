import { Card, NavLink } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom';

interface RestaurantCardProps {
    title: string;
    description: string;
}

const RestaurantCard = (props: RestaurantCardProps) => {
    let navigate = useNavigate();

    return (
        <Card className="clickable-card" onClick={() => navigate("/restaurants/123")} style={{cursor: "pointer"}}>
            <Card.Body>
                <Card.Title className="fs-6 fw-bold">{props.title}</Card.Title>
                <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
            </Card.Body>
        </Card>
    )
}

export default RestaurantCard