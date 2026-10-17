import { useState, type FormEvent } from "react";
import { Button, Container, Form } from "react-bootstrap";
import { updateRestaurant } from "../../api/updateRestaurant";

interface GeneralManagementProps {
    restaurant: Restaurant;
    onSaved: (restaurant: Restaurant) => void;
}

const GeneralManagement = ({ restaurant, onSaved }: GeneralManagementProps) => {
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [saved, setSaved] = useState(false);

    const submit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const form = new FormData(event.currentTarget);
        setSaving(true);
        setError("");
        setSaved(false);
        try {
            const updated = await updateRestaurant(restaurant.id, {
                name: String(form.get("name") ?? ""),
                description: String(form.get("description") ?? ""),
                address: String(form.get("address") ?? ""),
                telephone: String(form.get("telephone") ?? ""),
                openingHours: String(form.get("openingHours") ?? ""),
            });
            onSaved(updated);
            setSaved(true);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "Could not save restaurant");
        } finally {
            setSaving(false);
        }
    };

    return (
        <Container className="d-flex flex-column gap-4" style={{ maxWidth: "600px" }}>
            <Form key={restaurant.id} onSubmit={submit}>
                {([
                    ["name", "Name", restaurant.name],
                    ["description", "Description", restaurant.description],
                    ["address", "Address", restaurant.address],
                    ["telephone", "Telephone", restaurant.telephone],
                    ["openingHours", "Opening Hours", restaurant.openingHours],
                ] as const).map(([name, label, value]) => (
                    <Form.Group key={name} className="d-flex flex-column mb-3 gap-0" controlId={`restaurant-${name}`}>
                        <Form.Label className="text-secondary-emphasis fs-7">{label}</Form.Label>
                        <Form.Control as={name === "description" ? "textarea" : "input"} name={name} defaultValue={value} required={name !== "description"} className="fs-7" />
                    </Form.Group>
                ))}
                {error && <p role="alert" className="text-danger">{error}</p>}
                {saved && <p role="status" className="text-success">Saved</p>}
                <Button type="submit" variant="success" size="sm" disabled={saving}>{saving ? "Saving..." : "Save details"}</Button>
            </Form>
        </Container>
    );
};

export default GeneralManagement;
