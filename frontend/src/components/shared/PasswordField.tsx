import { useState } from 'react'
import { Button, Form } from 'react-bootstrap'
import { FaEye, FaEyeSlash } from 'react-icons/fa'

interface PasswordFieldProps {
    controlId: string;
    name: string;
    label: string;
    autoComplete: string;
}

const PasswordField = (props: PasswordFieldProps) => {
    const [showPassword, setShowPassword] = useState(false);

    return (
        <Form.Group className="d-flex flex-column mb-3 gap-1" controlId={props.controlId}>
            <Form.Label className="fs-7 mb-0">{props.label}</Form.Label>
            <div className="position-relative">
                <Form.Control type={showPassword ? 'text' : 'password'} name={props.name} required autoComplete={props.autoComplete} className="fs-7 bg-dark pe-5" />
                <Button variant="transparent" type="button" className="position-absolute top-0 end-0 h-100 border-0 text-secondary-emphasis" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword(!showPassword)}>
                    { showPassword ? <FaEyeSlash /> : <FaEye /> }
                </Button>
            </div>
        </Form.Group>
    )
}

export default PasswordField
