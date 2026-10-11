import axios from "axios";
import { setupInterceptors } from "./interceptors";

export const api = axios.create({
    baseURL: "http://localhost:8000/api/v1/",
    headers: {
        "Content-Type": "application/json",
    },
});

setupInterceptors(api);
