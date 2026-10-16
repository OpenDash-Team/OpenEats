import { Container, Form, InputGroup } from 'react-bootstrap'
import { IoMdSearch } from 'react-icons/io'
import RestaurantCard from '../components/discover_page/RestaurantCard'

import "./DiscoverPage.css";
import CustomerPageLayout from '../components/shared/CustomerPageLayout';

const DiscoverPage = () => {
  return (
    <CustomerPageLayout className="gap-4">
        <Container>
            <h2>What are you craving?</h2>
            <p className="text-secondary-emphasis">6 restaurants delivering to you</p>
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
                />
            </InputGroup>
        </Container>

        <Container className="d-flex flex-wrap gap-4 card-grid">
            <RestaurantCard 
                title = "Mama Rosa's Pizza"
                description = "Authentic Neapolitan pizza and homemade pasta baked in a wood-fired oven. Family recipes passed down three generations from Naples."
            />
        </Container>
    </CustomerPageLayout>
  )
}

export default DiscoverPage