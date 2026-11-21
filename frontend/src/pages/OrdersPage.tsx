import { Col, Container, Row } from 'react-bootstrap'
import OrderCard from '../components/orders_page/OrderCard'
import UserPageLayout from '../components/shared/UserPageLayout'

type Order = {
    id: string;
    restaurant: string;
    date: string;
    status: string;
    items: string[];
    total: number;
}

const OrdersPage = () => {
    const orders: Order[] = [
        { id: '1', restaurant: 'The Burger House', date: 'November 18, 2026', status: 'Delivered', items: ['Cheeseburger', 'French Fries'], total: 20.98 },
        { id: '2', restaurant: 'Pasta Kitchen', date: 'November 12, 2026', status: 'Delivered', items: ['Penne Alfredo', 'Garlic Bread'], total: 23.98 },
        { id: '3', restaurant: 'Pizza Corner', date: 'November 5, 2026', status: 'Delivered', items: ['Pepperoni Pizza'], total: 18.99 },
    ];

    return (
        <UserPageLayout className="gap-4">
            <Container>
                <h2>My Orders</h2>
                <p className="text-secondary-emphasis">View your past orders</p>
            </Container>

            <Container className="d-flex flex-column gap-3">
                    {
                        orders.map(
                            (order) =>
                            <OrderCard
                                key={order.id}
                                restaurant={order.restaurant}
                                date={order.date}
                                status={order.status}
                                items={order.items}
                                total={order.total}
                            />
                        )
                    }

                    { (orders.length === 0) &&
                        <p className="text-secondary-emphasis">You have no orders yet.</p>
                    }
            </Container>
        </UserPageLayout>
    )
}

export default OrdersPage
