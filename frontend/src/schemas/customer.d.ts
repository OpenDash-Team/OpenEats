interface Customer {
    id: string;
    name: string;
    email: string;
    telephone: string | null;
    address: string | null;
    role: "customer" | "owner";
    isActive: boolean;
}
