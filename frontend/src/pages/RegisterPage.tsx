import { useState, type FormEvent } from 'react'
import { Button, Col, Form, Row } from 'react-bootstrap'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import AuthPageLayout from '../components/shared/AuthPageLayout'
import PasswordField from '../components/shared/PasswordField'
import useLoggedIn from '../hooks/useLoggedIn'
import { registerCustomer } from '../api/registerCustomer'
import { login } from '../api/login'

const RegisterPage = () => {
    const navigate = useNavigate();
    const loginStatus = useLoggedIn();
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        const getValue = (name: string) => {
            const value = form.get(name);
            return typeof value === 'string' ? value : '';
        }
        setMessage('');

        if (form.get('password') !== form.get('confirmPassword')) {
            setMessage('Passwords do not match.');
            return;
        }

        setLoading(true);
        try {
            await registerCustomer({
                name: getValue('name'),
                email: getValue('email'),
                password: getValue('password'),
                telephone: getValue('telephone'),
                address: getValue('address'),
            });
        } catch (cause) {
            setMessage(cause instanceof Error && cause.message ? cause.message : 'Could not create account.');
            setLoading(false);
            return;
        }

        try {
            await login({ email: getValue('email'), password: getValue('password') });
            localStorage.setItem('userMode', 'customer');
            localStorage.setItem('restaurantId', '');
            window.location.replace('/');
        } catch {
            void navigate('/login', { replace: true });
        }
    }

    if (loginStatus === 'checking') return <p>Loading...</p>;
    if (loginStatus === 'error') return <p role="alert">Could not check your session. Please try again.</p>;
    if (loginStatus === 'loggedIn') return <Navigate to="/" replace />;

    return (
        <AuthPageLayout title="Register" maxWidth="640px">
            <Form onSubmit={onSubmit}>
                <Row>
                    <Col sm={6}>
                        <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerEmail">
                            <Form.Label className="fs-7 mb-0">Email</Form.Label>
                            <Form.Control type="email" name="email" required placeholder="you@example.com" autoComplete="email" className="fs-7 bg-dark" />
                        </Form.Group>

                        <PasswordField name="password" label="Password" autoComplete="new-password" />

                        <PasswordField name="confirmPassword" label="Confirm Password" autoComplete="new-password" />
                    </Col>

                    <Col sm={6}>
                        <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerName">
                            <Form.Label className="fs-7 mb-0">Name</Form.Label>
                            <Form.Control type="text" name="name" required placeholder="John Doe" autoComplete="name" className="fs-7 bg-dark" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerPhone">
                            <Form.Label className="fs-7 mb-0">Telephone (optional)</Form.Label>
                            <Form.Control type="tel" name="telephone" placeholder="+1 (234) 567-8900" autoComplete="tel" className="fs-7 bg-dark" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="registerAddress">
                            <Form.Label className="fs-7 mb-0">Address (optional)</Form.Label>
                            <Form.Control type="text" name="address" placeholder="123 Main Street" autoComplete="street-address" className="fs-7 bg-dark" />
                        </Form.Group>
                    </Col>
                </Row>

                <Button variant="light" type="submit" className="w-100 fs-7 fw-medium" disabled={loading}>{loading ? "Creating Account..." : "Create Account"}</Button>
                { message && <p role="alert" className="text-danger-emphasis fs-7 mt-3 mb-0">{message}</p> }
            </Form>

            <p className="text-center text-secondary-emphasis fs-7 mt-3 mb-0">Already have an account? <Link to="/login" className="text-body">Login</Link></p>
        </AuthPageLayout>
    )
}

export default RegisterPage
