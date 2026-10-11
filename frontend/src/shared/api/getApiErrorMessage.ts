import axios from "axios";

const toSafeMessage = (value: unknown): string => {
    if (typeof value === "string") return value;
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    if (Array.isArray(value)) {
        return value.map(toSafeMessage).filter(Boolean).join(", ");
    }
    if (value && typeof value === "object") {
        return Object.values(value).map(toSafeMessage).filter(Boolean).join(", ");
    }

    return "";
};

export const getApiErrorMessage = (error: unknown, fallback: string): string => {
    if (axios.isAxiosError(error) && error.response?.data) {
        const message = toSafeMessage(error.response.data).trim();
        if (message) {
            return message;
        }
    }

    if (error instanceof Error && error.message.trim()) {
        return error.message;
    }

    return fallback;
};
