import { Card } from 'react-bootstrap'

interface RestaurantCardProps {
    title: string;
    description: string;
    onClick?: () => void;
}

const RestaurantCard = (props: RestaurantCardProps) => {
    return (
        <Card className="clickable-card card-hover" onClick={props.onClick} style={{cursor: "pointer"}}>
            <Card.Body>
                <Card.Title className="fs-6 fw-bold">{props.title}</Card.Title>
                <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{props.description}</Card.Text>
            </Card.Body>
        </Card>
    )
}

export default RestaurantCard