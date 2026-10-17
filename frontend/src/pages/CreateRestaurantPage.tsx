import { Button, Container, Form } from "react-bootstrap";
import { IoAddCircleSharp } from "react-icons/io5";
import { useState, type FormEvent } from "react";
import { createRestaurant } from "../api/createRestaurant";

const CreateRestaurantPage = () => {
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");

    const submit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        setSaving(true);
        setError("");
        try {
            const restaurant = await createRestaurant({
                name: String(form.get("name") ?? ""),
                description: String(form.get("description") ?? ""),
                address: String(form.get("address") ?? ""),
                telephone: String(form.get("telephone") ?? ""),
                openingHours: String(form.get("openingHours") ?? ""),
            });
            localStorage.setItem("restaurantId", restaurant.id);
            window.location.replace("/");
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "Could not create restaurant");
            setSaving(false);
        }
    };
    const backToViewSelector = () => {
        localStorage.setItem("userMode", "");
        window.location.replace('/')
    }

    return (
        <div data-bs-theme="dark" className="min-vh-100 bg-dark text-white py-4 d-flex flex-column" style={{paddingInline: "8rem"}}>
            <Container className="d-flex flex-column align-items-center mt-4 gap-5">
                <Container className="d-flex flex-row justify-content-between gap-5">
                    <Button variant="outline-secondary" className="fs-7 mb-2" onClick = {backToViewSelector}>
                        Back to View Selector
                    </Button>

                    <h2> New Restaurant</h2>

                    <Button variant="success" type="submit" form="create-restaurant" disabled={saving} className="d-flex flew-row fs-7 align-items-center gap-2">
                        <IoAddCircleSharp className="fs-6" />
                        <p className="m-0 fs-7">{saving ? "Creating..." : "Create Restaurant"}</p>
                    </Button>

                </Container>

                <Container className="d-flex flex-column gap-4" style={{maxWidth: "400px"}}>
                    <Form id="create-restaurant" onSubmit={submit}>
                        <Form.Group className="d-flex flex-column mb-3 gap-0" controlId="restaurantName">
                            <Form.Label className="text-secondary-emphasis fs-7">Name</Form.Label>
                            <Form.Control type="text" name="name" required placeholder="Mama Rosa's Pizza" className="fs-7" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-0" controlId="restaurantDescription">
                            <Form.Label className="text-secondary-emphasis fs-7">Description</Form.Label>
                            <Form.Control as="textarea" name="description" placeholder="Tell customers about your restaurant..." className="fs-7" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-0" controlId="restaurantAddress">
                            <Form.Label className="text-secondary-emphasis fs-7">Address</Form.Label>
                            <Form.Control type="text" name="address" required placeholder="125 Boulevard Road" className="fs-7" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-0" controlId="restaurantTelephone">
                            <Form.Label className="text-secondary-emphasis fs-7">Telephone</Form.Label>
                            <Form.Control type="tel" name="telephone" required placeholder="+1 (234) 567-8900" className="fs-7" />
                        </Form.Group>

                        <Form.Group className="d-flex flex-column mb-3 gap-0" controlId="restaurantOpeningHours">
                            <Form.Label className="text-secondary-emphasis fs-7">Opening Hours</Form.Label>
                            <Form.Control type="text" name="openingHours" required placeholder="Tu,Th 16:00-20:00" className="fs-7" />
                        </Form.Group>
                        {error && <p role="alert" className="text-danger">{error}</p>}
                    </Form>
                </Container>
            </Container>
        </div>
    );
}

export default CreateRestaurantPage
