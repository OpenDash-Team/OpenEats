import { Container } from "react-bootstrap"
import { FaStore } from "react-icons/fa"
import { IoMdPeople } from "react-icons/io"
import ViewCard from "../components/mock_startup_page/ViewCard"
import { GiShoppingBag } from "react-icons/gi"

const MockStartupPage = () => {
    const setUserMode = (userMode: string) => {
        localStorage.setItem("userMode", userMode);
        localStorage.setItem("restaurantId", "");
        window.location.replace("/")
    }

    return (
        <div data-bs-theme="dark" className="min-vh-100 bg-dark text-white py-4 d-flex flex-column" style={{paddingInline: "8rem"}}>
            <Container className="d-flex flex-column align-items-center gap-5 mt-4">
                <Container className="d-flex flex-column align-items-center gap-2">
                    <IoMdPeople style={{fontSize: "4rem"}} />
                    <p className="fs-1 fw-bold"> Choose Your View </p>
                </Container>

                <Container className="d-flex flex-row justify-content-center gap-5">
                    <ViewCard icon={FaStore} title="Restaurant" onClick={ () => setUserMode("restaurant") } />
                    <ViewCard icon={GiShoppingBag} title="Customer" onClick={ () => setUserMode("customer") } />
                </Container>
            </Container>
        </div>
    )
}

export default MockStartupPage