import { useEffect, useState } from 'react';
import { Button } from 'react-bootstrap';

import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import { FaShoppingCart } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';
import { signOut } from '../../services/signOut';
import { fetchCustomer } from '../../api/fetchCustomer';

interface MyNavBarProps {
  customerName?: string;
}

const MyNavBar = (props: MyNavBarProps) => {
  const navigate = useNavigate();
  const [name, setName] = useState('');

  useEffect(() => {
    let active = true;
    fetchCustomer().then((customer) => {
      if (active) setName(customer.name);
    }).catch(() => {
      if (active) setName('');
    });
    return () => { active = false; };
  }, []);

  return (
    <Navbar bg="dark" data-bs-theme="dark" sticky="top" className="py-3 shadow-lg">
        <Container>
          <Navbar.Brand className="fw-bold" style={{cursor: "pointer"}} onClick={() => navigate("/")}>OpenEats</Navbar.Brand>
          <Nav className="m-auto d-row gap-4">
            <Nav.Link href="/" className="fs-7">Discover</Nav.Link>
            <Nav.Link href="/orders" className="fs-7">My Orders</Nav.Link>
            <Nav.Link href="/account" className="fs-7">Account</Nav.Link>
          </Nav>
          <div className="d-flex flex-row gap-4 text-body align-items-center fs-7">
            <Nav.Link href="/cart" className="d-flex gap-2 align-items-center"><FaShoppingCart /> Cart</Nav.Link>
            <div className="text-body vr"></div>
            <span className="text-secondary-emphasis">{props.customerName ?? name}</span>
            <Button variant="outline-danger" className="fs-7" onClick={signOut}>Sign Out</Button>
          </div>         
        </Container>
      </Navbar>
  )
}

export default MyNavBar