interface MenuSection {
    type: "MenuSection";
    id: string;
    name: string;
    description: string;
    hasMenuSection?: MenuSection | MenuSection[] | null;
    hasMenuItem: MenuItem | MenuItem[] | null;
}
