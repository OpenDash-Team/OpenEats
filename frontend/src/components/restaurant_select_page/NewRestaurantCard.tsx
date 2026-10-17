import { Card } from 'react-bootstrap'
import { IoAddCircleSharp } from 'react-icons/io5';

interface NewRestaurantCardProps {
    onClick?: () => void;
}

const RestaurantCard = (props: NewRestaurantCardProps) => {
    return (
        <Card className="clickable-card card-hover" onClick={props.onClick} style={{cursor: "pointer"}}>
            <Card.Body className="d-flex flex-row align-items-center justify-content-center gap-2">
                <IoAddCircleSharp className="fs-3" />
                <Card.Title className="fs-5 fw-bold m-0">New Restaurant</Card.Title>
            </Card.Body>
        </Card>
    )
}

export default RestaurantCard