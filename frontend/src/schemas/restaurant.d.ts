interface Restaurant {
    type: "Restaurant";
    id: string;
    name: string;
    description: string;
    address: string;
    telephone: string;
    openingHours: string;
    hasMenu: Menu | null;
}
