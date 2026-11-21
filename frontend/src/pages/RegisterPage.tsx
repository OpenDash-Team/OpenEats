import { useState, type FormEvent } from 'react'
import { Button, Form } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import AuthPageLayout from '../components/shared/AuthPageLayout'
import PasswordField from '../components/shared/PasswordField'

const RegisterPage = () => {
    const [message, setMessage] = useState('');

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);

        if (form.get('password') !== form.get('confirmPassword')) {
            setMessage('Passwords do not match.');
            return;
        }

        setMessage('Registration is not connected yet.');
    }

    return (
        <AuthPageLayout title="Register">
            <Form onSubmit={onSubmit}>
                <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerName">
                    <Form.Label className="fs-7 mb-0">Name</Form.Label>
                    <Form.Control type="text" name="name" required placeholder="John Doe" autoComplete="name" className="fs-7 bg-dark" />
                </Form.Group>

                <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerEmail">
                    <Form.Label className="fs-7 mb-0">Email</Form.Label>
                    <Form.Control type="email" name="email" required placeholder="you@example.com" autoComplete="email" className="fs-7 bg-dark" />
                </Form.Group>

                <PasswordField name="password" label="Password" autoComplete="new-password" />

                <PasswordField name="confirmPassword" label="Confirm Password" autoComplete="new-password" />

                <Button variant="light" type="submit" className="w-100 fs-7 fw-medium">Create Account</Button>
                { message && <p role="status" className="text-secondary-emphasis fs-7 mt-3 mb-0">{message}</p> }
            </Form>

            <p className="text-center text-secondary-emphasis fs-7 mt-3 mb-0">Already have an account? <Link to="/login" className="text-body">Login</Link></p>
        </AuthPageLayout>
    )
}

export default RegisterPage
