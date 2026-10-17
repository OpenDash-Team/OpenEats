import { Card } from 'react-bootstrap'
import type { IconType } from 'react-icons'

interface ViewCardProps {
    icon: IconType;
    title: string;
    onClick?: () => void;
}

const ViewCard = (props: ViewCardProps) => {
    return (
        <Card className="clickable-card card-hover" style={{width: "18rem", cursor: "pointer"}} onClick={props.onClick}>
            <Card.Body className="d-flex flex-column align-items-center gap-4 py-5">
                <props.icon className="fs-1" />
                <Card.Title className="fs-3">{props.title}</Card.Title>
            </Card.Body>
        </Card>
    )
}

export default ViewCard