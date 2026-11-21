import { useEffect, useState, type FormEvent } from 'react'
import { Button, Card, Col, Container, Form, Row } from 'react-bootstrap'
import UserPageLayout from '../components/shared/UserPageLayout'
import { fetchCustomer } from '../api/fetchCustomer'
import { updateCustomer } from '../api/updateCustomer'
import { deleteCustomer } from '../api/deleteCustomer'

import './AccountPage.css'

const AccountPage = () => {
    const [account, setAccount] = useState({ name: '', email: '', telephone: '', address: '' });
    const [savedAccount, setSavedAccount] = useState(account);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [editMode, setEditMode] = useState(false);
    const [confirmDelete, setConfirmDelete] = useState(false);

    useEffect(() => {
        let active = true;

        fetchCustomer().then((customer) => {
            if (!active) return;
            const details = { name: customer.name, email: customer.email, telephone: customer.telephone ?? '', address: customer.address ?? '' };
            setAccount(details);
            setSavedAccount(details);
            setLoading(false);
        }).catch((cause) => {
            if (!active) return;
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not load account.');
            setLoading(false);
        });

        return () => { active = false; };
    }, []);

    const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError('');
        setMessage('');

        if ((savedAccount.telephone && !account.telephone.trim()) || (savedAccount.address && !account.address.trim())) {
            setError('Telephone and address cannot currently be cleared.');
            return;
        }

        setSaving(true);
        try {
            const customer = await updateCustomer({
                name: account.name,
                email: account.email,
                telephone: account.telephone.trim() || null,
                address: account.address.trim() || null,
            });
            const details = { name: customer.name, email: customer.email, telephone: customer.telephone ?? '', address: customer.address ?? '' };
            setAccount(details);
            setSavedAccount(details);
            setMessage('Changes saved.');
            setEditMode(false);
        } catch (cause) {
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not save changes.');
        } finally {
            setSaving(false);
        }
    }

    const onDiscard = () => {
        setAccount(savedAccount);
        setEditMode(false);
        setMessage('');
        setError('');
    }

    const onDelete = async () => {
        setError('');
        setSaving(true);
        try {
            await deleteCustomer();
            localStorage.removeItem('token');
            localStorage.removeItem('userMode');
            localStorage.removeItem('restaurantId');
            window.location.replace('/login');
        } catch (cause) {
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not delete account.');
            setSaving(false);
        }
    }

    return (
        <UserPageLayout className="gap-4" customerName={savedAccount.name || undefined}>
            <Container>
                <h2>Account</h2>
                <p className="text-secondary-emphasis">Manage your account information</p>
            </Container>

            <Container>
                <Card>
                    <Card.Body>
                        { loading && <p className="text-secondary-emphasis">Loading...</p> }
                        { error && <p role="alert" className="text-danger">{error}</p> }
                        { !loading && (savedAccount.email !== '') && <>
                        <Form onSubmit={onSubmit}>
                            <Row>
                                <Col sm={6}>
                                    <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="accountEmail">
                                        <Form.Label className="fs-7 mb-0">Email</Form.Label>
                                        <Form.Control disabled={!editMode || saving} type="email" required autoComplete="email" className="fs-7 account-input" value={account.email} onChange={(event) => setAccount({ ...account, email: event.target.value })} />
                                    </Form.Group>
                                </Col>

                                <Col sm={6}>
                                    <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="accountName">
                                        <Form.Label className="fs-7 mb-0">Name</Form.Label>
                                        <Form.Control disabled={!editMode || saving} type="text" required autoComplete="name" className="fs-7 account-input" value={account.name} onChange={(event) => setAccount({ ...account, name: event.target.value })} />
                                    </Form.Group>

                                    <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="accountTelephone">
                                        <Form.Label className="fs-7 mb-0">Telephone</Form.Label>
                                        <Form.Control disabled={!editMode || saving} type="tel" autoComplete="tel" className="fs-7 account-input" value={account.telephone} onChange={(event) => setAccount({ ...account, telephone: event.target.value })} />
                                    </Form.Group>

                                    <Form.Group className="d-flex flex-column mb-3 gap-1" controlId="accountAddress">
                                        <Form.Label className="fs-7 mb-0">Address</Form.Label>
                                        <Form.Control disabled={!editMode || saving} type="text" autoComplete="street-address" className="fs-7 account-input" value={account.address} onChange={(event) => setAccount({ ...account, address: event.target.value })} />
                                    </Form.Group>
                                </Col>
                            </Row>

                            { !editMode &&
                                <Button variant="light" type="button" className="fs-7 fw-medium" onClick={() => { setEditMode(true); setMessage(''); }}>Edit</Button>
                            }
                            { editMode &&
                                <div className="d-flex gap-2">
                                    <Button variant="light" type="submit" className="fs-7 fw-medium" disabled={saving}>Save Changes</Button>
                                    <Button variant="outline-secondary" type="button" className="fs-7" disabled={saving} onClick={onDiscard}>Discard</Button>
                                </div>
                            }
                            { message && <p role="status" className="text-secondary-emphasis fs-7 mt-3 mb-0">{message}</p> }
                        </Form>

                        <hr />
                        { confirmDelete ?
                            <div>
                                <p className="fs-7">Are you sure you want to delete your account?</p>
                                <div className="d-flex gap-2">
                                    <Button variant="danger" className="fs-7" disabled={saving} onClick={onDelete}>Delete Account</Button>
                                    <Button variant="outline-secondary" className="fs-7" disabled={saving} onClick={() => setConfirmDelete(false)}>Cancel</Button>
                                </div>
                            </div>
                            : <Button variant="outline-danger" className="fs-7" onClick={() => setConfirmDelete(true)}>Delete Account</Button>
                        }
                        </> }
                    </Card.Body>
                </Card>
            </Container>
        </UserPageLayout>
    )
}

export default AccountPage
