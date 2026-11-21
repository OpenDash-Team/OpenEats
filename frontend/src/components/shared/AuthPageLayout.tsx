import { Card } from 'react-bootstrap'
import { type ReactNode } from 'react'
import { Link } from 'react-router-dom'

interface AuthPageLayoutProps {
    title: string;
    children: ReactNode;
}

const AuthPageLayout = (props: AuthPageLayoutProps) => {
    return (
        <main data-bs-theme="dark" className="min-vh-100 bg-dark text-body d-flex align-items-center justify-content-center px-3 py-5">
            <div className="w-100 d-flex flex-column align-items-center gap-4" style={{maxWidth: "400px", transform: "translateY(-3rem)"}}>
                <Link to="/" className="fs-4 fw-bold text-body text-decoration-none">OpenEats</Link>
                <Card className="w-100 rounded-4 shadow-lg">
                    <Card.Body className="p-3">
                        <h1 className="text-center fs-4 fw-semibold mb-4">{props.title}</h1>
                        {props.children}
                    </Card.Body>
                </Card>
            </div>
        </main>
    )
}

export default AuthPageLayout
