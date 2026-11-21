import { request } from "./request";

export async function logout(): Promise<void> {
    const token = localStorage.getItem("token");

    try {
        await request<{ message: string }>("/logout", { method: "POST" });
    } finally {
        if (localStorage.getItem("token") === token) localStorage.removeItem("token");
    }
}
