import { useState } from 'react'
import { Button, Col, Container, Row } from 'react-bootstrap'
import { useNavigate } from 'react-router-dom'
import CartItemCard from '../components/cart_page/CartItemCard'
import CartSummary from '../components/cart_page/CartSummary'
import UserPageLayout from '../components/shared/UserPageLayout'

type CartItem = {
    id: string;
    name: string;
    description: string;
    price: number;
    quantity: number;
}

const CartPage = () => {
    const navigate = useNavigate();
    const [items, setItems] = useState<CartItem[]>([
        { id: "1", name: 'Cheeseburger', description: 'Beef patty, cheddar, lettuce and tomato', price: 14.99, quantity: 1 },
        { id: "2", name: 'French Fries', description: 'Crispy fries with sea salt', price: 5.99, quantity: 2 },
        { id: "3", name: 'Chocolate Milkshake', description: 'Creamy chocolate milkshake', price: 6.99, quantity: 1 },
    ]);
    const total = items.reduce((sum, item) => sum + item.price * item.quantity, 0);

    const updateQuantity = (itemId: string, change: number) => {
        const updated = [...items];

        for (const item of updated) {
            if (item.id === itemId) {
                item.quantity = Math.max(1, item.quantity + change);
            }
        }

        setItems(updated);
    }

    const onRemove = (itemId: string) => {
        setItems((current) => current.filter((item) => item.id !== itemId))
    }

    return (
        <UserPageLayout className="gap-4">
            <Container>
                <h2>Your Cart</h2>
                <p className="text-secondary-emphasis">Review your order before checkout</p>
            </Container>

            <Container>
                <Row className="g-4">
                    <Col md={8} className="d-flex flex-column gap-3">
                        {
                            items.map(
                                (item) => 
                                <CartItemCard 
                                    key={item.id} 
                                    name={item.name} 
                                    description={item.description} 
                                    price={item.price} 
                                    quantity={item.quantity} 
                                    onDecrease={() => updateQuantity(item.id, -1)} 
                                    onIncrease={() => updateQuantity(item.id, 1)} 
                                    onRemove={() => onRemove(item.id)} 
                                />
                            )
                        }

                        { (items.length === 0) && 
                            <p className="text-secondary-emphasis">Your cart is empty.</p> 
                        }
                    </Col>

                    <Col md={4}>
                        <CartSummary total={total} onCheckout={() => console.log("Checkout")} />
                    </Col>
                </Row>
            </Container>
        </UserPageLayout>
    )
}

export default CartPage
