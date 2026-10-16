import { type ReactNode } from 'react'
import { Container } from 'react-bootstrap';

interface MenuSectionProps {
    children?: ReactNode;
    title: string;
}

const MenuSection = (props: MenuSectionProps) => {
  return (
    <Container className="d-flex flex-column gap-1">
        <h5 className="fw-bold">{props.title}</h5>
        <Container className="d-flex flex-column gap-4">
            {props.children}
        </Container>
    </Container>
  )
}

export default MenuSection