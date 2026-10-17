interface MenuItem {
    type: "MenuItem";
    id: string;
    name: string;
    description: string;
    suitableForDiet: RestrictedDiet | RestrictedDiet[];
    offers: Offer | Offer[]
}