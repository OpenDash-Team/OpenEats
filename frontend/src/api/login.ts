import { request } from "./request";

type LoginRequest = {
    email: string;
    password: string;
};

export async function login(data: LoginRequest): Promise<Token> {
    const result = await request<Token>("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });
    localStorage.setItem("token", result.access_token);
    return result;
}
