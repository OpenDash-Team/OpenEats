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
    const response = await fetch(`/api${path}`, init);

    if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(errorMessage(body?.detail, response.status));
    }

    return response.status === 204 ? undefined as T : response.json() as Promise<T>;
}
