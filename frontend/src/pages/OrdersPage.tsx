import { useEffect, useState } from 'react'
import { Container } from 'react-bootstrap'
import OrderCard from '../components/orders_page/OrderCard'
import UserPageLayout from '../components/shared/UserPageLayout'
import { fetchOrders } from '../api/fetchOrders'
import { fetchRestaurants } from '../api/fetchRestaurants'

const OrdersPage = () => {
    const [orders, setOrders] = useState<Order[]>([]);
    const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        let active = true;

        fetchOrders().then((result) => {
            if (active) setOrders(result);
        }).catch((cause) => {
            if (active) setError(cause instanceof Error && cause.message ? cause.message : 'Could not load orders.');
        }).finally(() => {
            if (active) setLoading(false);
        });

        fetchRestaurants().then((result) => {
            if (active) setRestaurants(result);
        }).catch(() => {});

        return () => { active = false; };
    }, []);

    return (
        <UserPageLayout className="gap-4">
            <Container>
                <h2>My Orders</h2>
                <p className="text-secondary-emphasis">View your past orders</p>
            </Container>

            <Container className="d-flex flex-column gap-3">
                    { loading && <p className="text-secondary-emphasis">Loading...</p> }
                    { error && <p role="alert" className="text-danger">{error}</p> }
                    {
                        orders.map(
                            (order) =>
                            <OrderCard
                                key={order.id}
                                restaurant={restaurants.find((restaurant) => restaurant.id === order.restaurantId)?.name ?? 'Restaurant unavailable'}
                                date={new Date(order.createdAt).toLocaleDateString()}
                                status={order.status}
                                items={order.items.map((item) => `${item.quantity} × ${item.name}`)}
                                total={order.total}
                                currency={order.currency}
                            />
                        )
                    }

                    { (!loading && !error && orders.length === 0) &&
                        <p className="text-secondary-emphasis">You have no orders yet.</p>
                    }
            </Container>
        </UserPageLayout>
    )
}

export default OrdersPage
