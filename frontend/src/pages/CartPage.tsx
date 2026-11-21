import { useEffect, useState } from 'react'
import { Button, Card, Col, Container, Row } from 'react-bootstrap'
import CartItemCard from '../components/cart_page/CartItemCard'
import CartSummary from '../components/cart_page/CartSummary'
import UserPageLayout from '../components/shared/UserPageLayout'
import { fetchCart } from '../api/fetchCart'
import { updateCartItem } from '../api/updateCartItem'
import { removeCartItem } from '../api/removeCartItem'
import { clearCart } from '../api/clearCart'
import { checkout } from '../api/checkout'

const CartPage = () => {
    const [cart, setCart] = useState<Cart | null>(null);
    const [order, setOrder] = useState<Order | null>(null);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(true);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        let active = true;

        fetchCart().then((result) => {
            if (active) setCart(result);
        }).catch((cause) => {
            if (active) setError(cause instanceof Error && cause.message ? cause.message : 'Could not load cart.');
        }).finally(() => {
            if (active) setLoading(false);
        });

        return () => { active = false; };
    }, []);

    const updateCart = async (action: () => Promise<Cart>) => {
        if (busy) return;
        setBusy(true);
        setError('');

        try {
            setCart(await action());
        } catch (cause) {
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not update cart.');
        } finally {
            setBusy(false);
        }
    }

    const updateQuantity = (item: CartItem, change: number) => {
        const quantity = Math.max(1, Math.min(99, item.quantity + change));
        if (quantity !== item.quantity) void updateCart(() => updateCartItem(item.menuItemId, quantity));
    }

    const onCheckout = async () => {
        if (busy) return;
        setBusy(true);
        setError('');

        try {
            setOrder(await checkout());
            setCart(null);
        } catch (cause) {
            setError(cause instanceof Error && cause.message ? cause.message : 'Could not check out.');
        } finally {
            setBusy(false);
        }
    }

    return (
        <UserPageLayout className="gap-4">
            <Container>
                <h2>Your Cart</h2>
                <p className="text-secondary-emphasis">Review your order before checkout</p>
            </Container>

            <Container>
                { loading && <p className="text-secondary-emphasis">Loading...</p> }
                { error && <p role="alert" className="text-danger">{error}</p> }
                { order &&
                    <Card>
                        <Card.Body>
                            <Card.Title className="fs-6 fw-bold">Order placed</Card.Title>
                            <Card.Text className="fs-7 text-secondary-emphasis">Order {order.id}</Card.Text>
                            {order.items.map((item) => <p key={item.menuItemId} className="fs-7 mb-1">{item.quantity} × {item.name} — {item.lineTotal} {order.currency}</p>)}
                            <p className="fs-7 mt-3 mb-1">Total: {order.total} {order.currency}</p>
                            <p className="fs-7 mb-0">Delivery address: {order.deliveryAddress}</p>
                        </Card.Body>
                    </Card>
                }
                { cart &&
                    <Row className="g-4">
                        <Col md={8} className="d-flex flex-column gap-3">
                            {
                                cart.items.map(
                                    (item) =>
                                    <CartItemCard
                                        key={item.menuItemId}
                                        name={item.name ?? 'Item no longer available'}
                                        lineTotal={item.lineTotal}
                                        currency={cart.currency}
                                        quantity={item.quantity}
                                        available={item.available}
                                        busy={busy}
                                        onDecrease={() => updateQuantity(item, -1)}
                                        onIncrease={() => updateQuantity(item, 1)}
                                        onRemove={() => updateCart(() => removeCartItem(item.menuItemId))}
                                    />
                                )
                            }

                            { (cart.items.length === 0) &&
                                <p className="text-secondary-emphasis">Your cart is empty.</p>
                            }
                            { (cart.items.length > 0) &&
                                <Button variant="outline-danger" className="fs-7 align-self-start" disabled={busy} onClick={() => updateCart(clearCart)}>Clear Cart</Button>
                            }
                        </Col>

                        <Col md={4}>
                            <CartSummary subtotal={cart.subtotal} total={cart.total} currency={cart.currency} disabled={busy || cart.items.length === 0 || cart.items.some((item) => !item.available)} onCheckout={onCheckout} />
                        </Col>
                    </Row>
                }
            </Container>
        </UserPageLayout>
    )
}

export default CartPage
