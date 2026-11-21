import { useState, type FormEvent } from 'react'
import { Button, Form } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import AuthPageLayout from '../components/shared/AuthPageLayout'
import PasswordField from '../components/shared/PasswordField'

import "./LoginPage.css";

type DemoAccount = {
    role: string;
    email: string;
    password: string;
}

const LoginPage = () => {
    const [email, setEmail] = useState("")
    const [password, setPassword] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const onSubmit = (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setSubmitted(true);
    }

    const demoAccounts: DemoAccount[] = [
        {role: "Customer", email: "customer@openeats.com", password: "password123"},
        {role: "Owner", email: "owner@openeats.com", password: "password123"},
    ]

    const selectDemoAccount = (account: DemoAccount) => {
        setEmail(account.email);
        setPassword(account.password);
    }

    return (
        <AuthPageLayout title="Login">
            <Form onSubmit={onSubmit}>
                <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="loginEmail">
                    <Form.Label className="fs-7 mb-0">Email</Form.Label>
                    <Form.Control type="email" name="email" required placeholder="you@example.com" autoComplete="email" className="fs-7 bg-dark" value={email} onChange={(event) => setEmail(event.target.value)} />
                </Form.Group>

                <PasswordField name="password" label="Password" autoComplete="current-password" value={password} onChange={setPassword} />

                <Button variant="light" type="submit" className="w-100 fs-7 fw-medium">Login</Button>
                { submitted && <p role="status" className="text-secondary-emphasis fs-7 mt-3 mb-0">Sign in is not connected yet.</p> }
            </Form>

            <p className="text-center text-secondary-emphasis fs-7 mt-3 mb-0">Don't have an account? <Link to="/register" className="text-body">Register</Link></p>

            <hr />

            <div className="d-flex flex-column">
                <p className="text-secondary-emphasis fs-6">Demo Accounts</p>
                {
                    demoAccounts.map(
                        (account) => 
                        <Button 
                            variant="transparent" 
                            className="text-primary-emphasis fs-7 demo-account"
                            onClick={() => selectDemoAccount(account)}
                        >
                            {account.role}
                            <span className="text-secondary-emphasis ms-2 fs-8">
                                {account.email} / {account.password}
                            </span>
                        </Button>
                    )
                }
                
            </div>
        </AuthPageLayout>
    )
}

export default LoginPage
