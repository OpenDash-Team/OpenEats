import { Container, Form, InputGroup } from 'react-bootstrap'
import { IoMdSearch } from 'react-icons/io'
import RestaurantCard from '../components/discover_page/RestaurantCard'
import UserPageLayout from '../components/shared/UserPageLayout';

import "./DiscoverPage.css";
import { useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { fetchRestaurants } from '../api/fetchRestaurants';

const DiscoverPage = () => {
    const navigate = useNavigate();
    const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
    const [search, setSearch] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        let active = true;
        fetchRestaurants({ name: search }).then((results) => {
            if (active) { setRestaurants(results); setError(''); }
        }).catch((cause) => {
            if (active) setError(cause instanceof Error ? cause.message : 'Could not load restaurants');
        });
        return () => { active = false; };
    }, [search]);

    return (
        <UserPageLayout className="gap-4">
            <Container>
                <h2>What are you craving?</h2>
                <p className="text-secondary-emphasis">{restaurants.length} restaurants available</p>
            </Container>

            <Container>
                <InputGroup>
                    <InputGroup.Text>
                        <IoMdSearch />
                    </InputGroup.Text>

                    <Form.Control
                        type="search"
                        placeholder="Search"
                        aria-label="Search"
                        className="py-2 fs-7"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                    />
                </InputGroup>
            </Container>

            {error && <p role="alert" className="text-danger">{error}</p>}
            <Container className="d-flex flex-wrap gap-4 card-grid">
                {restaurants.map((restaurant) => <RestaurantCard key={restaurant.id} title={restaurant.name} description={restaurant.description} onClick={() => navigate(`/restaurants/${restaurant.id}`)} />)}
            </Container>
        </UserPageLayout>
    )
}

export default DiscoverPage
