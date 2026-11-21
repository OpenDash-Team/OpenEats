const API_VERSION = 1;

function errorMessage(detail: unknown, status: number): string {
    if (typeof detail === "string") return detail;

    if (Array.isArray(detail)) {
        const messages = detail.map((entry: unknown) => {
            if (typeof entry !== "object" || entry === null || !("msg" in entry) || typeof entry.msg !== "string") return null;
            const location = "loc" in entry && Array.isArray(entry.loc)
                ? entry.loc.filter((part: unknown) => part !== "body").join(".")
                : "";
            return location ? `${location}: ${entry.msg}` : entry.msg;
        }).filter((message): message is string => message !== null);
        if (messages.length > 0) return messages.join("; ");
    }

    return `Request failed (${status})`;
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
    const token = localStorage.getItem("token");
    const headers = new Headers(init?.headers);

    if (token && path !== "/login" && path !== "/customers" && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetch(`/api/v${API_VERSION}${path}`, { ...init, headers });

    if (!response.ok) {
        if (response.status === 401 && token && headers.get("Authorization") === `Bearer ${token}` && localStorage.getItem("token") === token) {
            localStorage.removeItem("token");
            localStorage.removeItem("userMode");
            window.dispatchEvent(new Event("session-expired"));
        }
        const body = await response.json().catch(() => null);
        throw new Error(errorMessage(body?.detail, response.status));
    }

    return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
