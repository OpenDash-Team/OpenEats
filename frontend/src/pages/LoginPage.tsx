import { useState, type FormEvent } from 'react'
import { Button, Form } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import AuthPageLayout from '../components/shared/AuthPageLayout'
import PasswordField from '../components/shared/PasswordField'

const LoginPage = () => {
    const [submitted, setSubmitted] = useState(false);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSubmitted(true);
    }

    return (
        <AuthPageLayout title="Login">
            <Form onSubmit={onSubmit}>
                <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="loginEmail">
                    <Form.Label className="fs-7 mb-0">Email</Form.Label>
                    <Form.Control type="email" name="email" required placeholder="you@example.com" autoComplete="email" className="fs-7 bg-dark" />
                </Form.Group>

                <PasswordField controlId="loginPassword" name="password" label="Password" autoComplete="current-password" />

                <Button variant="light" type="submit" className="w-100 fs-7 fw-medium">Login</Button>
                { submitted && <p role="status" className="text-secondary-emphasis fs-7 mt-3 mb-0">Sign in is not connected yet.</p> }
            </Form>

            <p className="text-center text-secondary-emphasis fs-7 mt-3 mb-0">Don't have an account? <Link to="/register" className="text-body">Register</Link></p>
        </AuthPageLayout>
    )
}

export default LoginPage
