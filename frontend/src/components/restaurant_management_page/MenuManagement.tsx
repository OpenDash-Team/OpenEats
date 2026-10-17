import { useState, type FormEvent } from "react";
import { Badge, Button, Card, Container, Form } from "react-bootstrap";
import { createMenuItem } from "../../api/createMenuItem";
import { updateMenuItem } from "../../api/updateMenuItem";
import { deleteMenuItem } from "../../api/deleteMenuItem";
import { fetchRestaurantDetails } from "../../api/fetchRestaurantDetails";

const asArray = <T,>(value: T | T[] | null | undefined): T[] =>
    value == null ? [] : Array.isArray(value) ? value : [value];

const inStock = "https://schema.org/InStock" as ItemAvailability;
const outOfStock = "https://schema.org/OutOfStock" as ItemAvailability;

const dietOptions: { label: string; value: RestrictedDiet }[] = [
    ["Diabetic", "DiabeticDiet"], ["Gluten free", "GlutenFreeDiet"],
    ["Halal", "HalalDiet"], ["Hindu", "HinduDiet"],
    ["Kosher", "KosherDiet"], ["Low calorie", "LowCalorieDiet"],
    ["Low fat", "LowFatDiet"], ["Low lactose", "LowLactoseDiet"],
    ["Low salt", "LowSaltDiet"], ["Vegan", "VeganDiet"],
    ["Vegetarian", "VegetarianDiet"],
].map(([label, name]) => ({ label, value: `https://schema.org/${name}` as RestrictedDiet }));

interface EditableMenuItemProps {
    item: MenuItem;
    isNew?: boolean;
    onSave: (item: MenuItem) => Promise<void>;
    onRemove: () => Promise<void> | void;
}

const EditableMenuItem = ({ item, isNew = false, onSave, onRemove }: EditableMenuItemProps) => {
    const [editing, setEditing] = useState(isNew);
    const [draft, setDraft] = useState(item);
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const offer = asArray(draft.offers)[0];
    const savedOffer = asArray(item.offers)[0];

    const updateOffer = (changes: Partial<Offer>) => {
        setDraft((current) => {
            const [first, ...otherOffers] = asArray(current.offers);
            return { ...current, offers: [{ ...first, ...changes }, ...otherOffers] };
        });
    };

    const save = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setBusy(true);
        setError("");
        try {
            await onSave(draft);
            setEditing(false);
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "Could not save item");
        } finally {
            setBusy(false);
        }
    };

    const remove = async () => {
        setBusy(true);
        setError("");
        try {
            await onRemove();
        } catch (cause) {
            setError(cause instanceof Error ? cause.message : "Could not remove item");
            setBusy(false);
        }
    };

    return (
        <Card>
            <Card.Body>
                {!editing ? (
                    <>
                        <Card.Title className="fs-6 fw-bold d-flex flex-wrap align-items-center gap-2">
                            {item.name} <Badge bg="secondary">{savedOffer.priceCurrency} {Number(savedOffer.price).toFixed(2)}</Badge>
                        </Card.Title>
                        {item.description && <Card.Text className="line-clamp-2 fs-8 text-secondary-emphasis">{item.description}</Card.Text>}
                        {savedOffer.availability === outOfStock && <p className="fs-8 text-secondary mb-2">Out of stock</p>}
                        <Button variant="outline-success" size="sm" className="fs-8" onClick={() => { setDraft(item); setEditing(true); }}>Edit</Button>
                    </>
                ) : (
                    <Form className="d-flex flex-column gap-3" onSubmit={(event) => void save(event)}>
                        <div className="d-flex justify-content-between align-items-center gap-2">
                            <h4 className="fs-6 fw-semibold m-0">{isNew ? "New item" : "Edit item"}</h4>
                            {!isNew && <Button variant="link" size="sm" className="text-danger p-0" disabled={busy} onClick={() => void remove()}>Remove</Button>}
                        </div>
                        <Form.Group controlId={`item-name-${item.id}`}>
                            <Form.Label className="text-secondary-emphasis fs-7">Name</Form.Label>
                            <Form.Control className="fs-7" required value={draft.name} onChange={(event) => setDraft((current) => ({ ...current, name: event.target.value }))} />
                        </Form.Group>
                        <Form.Group controlId={`item-description-${item.id}`}>
                            <Form.Label className="text-secondary-emphasis fs-7">Description</Form.Label>
                            <Form.Control as="textarea" rows={2} className="fs-7" value={draft.description} onChange={(event) => setDraft((current) => ({ ...current, description: event.target.value }))} />
                        </Form.Group>
                        <div className="d-flex flex-wrap gap-3">
                            <Form.Group controlId={`item-price-${item.id}`} className="flex-grow-1">
                                <Form.Label className="text-secondary-emphasis fs-7">Price ({offer.priceCurrency})</Form.Label>
                                <Form.Control type="number" min="0" step="0.01" className="fs-7" required value={offer.price} onChange={(event) => updateOffer({ price: Number(event.target.value) })} />
                            </Form.Group>
                            <Form.Group controlId={`item-availability-${item.id}`} className="flex-grow-1">
                                <Form.Label className="text-secondary-emphasis fs-7">Availability</Form.Label>
                                <Form.Select className="fs-7" value={offer.availability} onChange={(event) => updateOffer({ availability: event.target.value as ItemAvailability })}>
                                    <option value={inStock}>In stock</option>
                                    <option value={outOfStock}>Out of stock</option>
                                </Form.Select>
                            </Form.Group>
                        </div>
                        <Form.Group controlId={`item-diet-${item.id}`}>
                            <Form.Label className="text-secondary-emphasis fs-7">Suitable for diets</Form.Label>
                            <Form.Select multiple className="fs-7" value={asArray(draft.suitableForDiet)} onChange={(event) => setDraft((current) => ({ ...current, suitableForDiet: Array.from(event.target.selectedOptions, (option) => option.value as RestrictedDiet) }))}>
                                {dietOptions.map((diet) => <option key={diet.value} value={diet.value}>{diet.label}</option>)}
                            </Form.Select>
                            <Form.Text>Hold Ctrl or Command to select multiple diets.</Form.Text>
                        </Form.Group>
                        <div className="d-flex gap-2">
                            <Button type="submit" variant="success" size="sm" disabled={busy}>{busy ? "Saving..." : "Save"}</Button>
                            <Button variant="outline-secondary" size="sm" disabled={busy} onClick={() => isNew ? void onRemove() : setEditing(false)}>Cancel</Button>
                        </div>
                    </Form>
                )}
                {error && <p role="alert" className="text-danger mt-2 mb-0">{error}</p>}
            </Card.Body>
        </Card>
    );
};

interface MenuManagementProps {
    restaurant: Restaurant;
    onChanged: (restaurant: Restaurant) => void;
}

const MenuManagement = ({ restaurant, onChanged }: MenuManagementProps) => {
    const [adding, setAdding] = useState(false);
    const sections = asArray(restaurant.hasMenu?.hasMenuSection);
    const refresh = async () => onChanged(await fetchRestaurantDetails(restaurant.id));
    const newItem: MenuItem = {
        type: "MenuItem", id: "new", name: "", description: "", suitableForDiet: [],
        offers: [{ type: "Offer", price: 0, priceCurrency: "CAD", availability: inStock }],
    };

    const renderSection = (section: MenuSection) => (
        <section key={section.id} className="d-flex flex-column gap-3 border-top pt-4">
            <h3 className="fs-6 fw-semibold m-0">{section.name}</h3>
            {section.description && <p className="text-secondary fs-7 m-0">{section.description}</p>}
            {asArray(section.hasMenuItem).map((item) => (
                <EditableMenuItem
                    key={item.id}
                    item={item}
                    onSave={async (savedItem) => {
                        await updateMenuItem(restaurant.id, item.id, { name: savedItem.name, description: savedItem.description, suitableForDiet: savedItem.suitableForDiet, offers: savedItem.offers });
                        await refresh();
                    }}
                    onRemove={async () => { await deleteMenuItem(restaurant.id, item.id); await refresh(); }}
                />
            ))}
            {asArray(section.hasMenuSection).map(renderSection)}
        </section>
    );

    return (
        <Container className="d-flex flex-column gap-4" style={{ maxWidth: "600px" }}>
            <div className="d-flex align-items-center justify-content-between gap-3">
                <h2 className="fs-5 fw-semibold m-0">Menu</h2>
                <Button variant="outline-success" size="sm" disabled={adding} onClick={() => setAdding(true)}>Add item</Button>
            </div>
            {adding && <EditableMenuItem item={newItem} isNew onSave={async (item) => {
                await createMenuItem(restaurant.id, { name: item.name, description: item.description, suitableForDiet: item.suitableForDiet, offers: item.offers });
                await refresh();
                setAdding(false);
            }} onRemove={() => setAdding(false)} />}
            {sections.length === 0 && !adding && <p className="text-secondary fs-7 m-0">No menu items yet.</p>}
            {sections.map(renderSection)}
        </Container>
    );
};

export default MenuManagement;
