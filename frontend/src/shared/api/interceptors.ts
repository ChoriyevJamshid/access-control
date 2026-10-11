import axios, { type AxiosInstance } from "axios";

export function setupInterceptors(api: AxiosInstance) {
    // Добавляем access-токен к каждому запросу
    api.interceptors.request.use((config) => {
        const token = localStorage.getItem("access");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    });

    // При 401 — пробуем обновить токен через /api/token/refresh/
    api.interceptors.response.use(
        (response) => response,
        async (error) => {
            const originalRequest = error.config;
            if (
                error.response?.status === 401 &&
                !originalRequest._retry
            ) {
                originalRequest._retry = true;
                try {
                    const refresh = localStorage.getItem("refresh");
                    const { data } = await axios.post(
                        "http://localhost:8000/api/token/refresh/",
                        { refresh }
                    );
                    localStorage.setItem("access", data.access);
                    originalRequest.headers.Authorization = `Bearer ${data.access}`;
                    return api(originalRequest);
                } catch {
                    localStorage.removeItem("access");
                    localStorage.removeItem("refresh");
                    window.location.href = "/login";
                }
            }
            return Promise.reject(error);
        }
    );
}
