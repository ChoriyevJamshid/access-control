import { api } from "@/shared/api/axios";

export interface DashboardActivityDay {
    date: string;
    present_count: number;
    total_work_seconds: number;
    total_late_seconds: number;
}

export interface DashboardData {
    total_employees: number;
    total_departments: number;
    today_present: number;
    today_present_percent: number;
    today_present_change_percent: number;
    today_late: number;
    today_late_percent: number;
    today_late_change_percent: number;
    activity_7_days: DashboardActivityDay[];
    alerts: string[];
    as_of: string;
    timezone: string;
}

type ApiMessage = {
    level?: string;
    code?: string;
    message?: unknown;
};

interface DashboardApiResponseNew {
    summary: {
        total_employees: number;
        total_departments: number;
        today_present: number;
        today_present_percent: number;
        today_present_change_percent: number;
        today_late: number;
        today_late_percent: number;
        today_late_change_percent: number;
    };
    series: {
        activity_7_days: DashboardActivityDay[];
    };
    alerts: unknown[];
    meta: {
        as_of: string;
        timezone: string;
    };
}

interface DashboardApiResponseOld {
    total_employees: number;
    total_departments: number;
    today_present: number;
    today_present_change_percent: number;
    today_late: number;
    today_late_change_percent: number;
    activity_7_days: DashboardActivityDay[];
}

const toSafeText = (value: unknown): string => {
    if (typeof value === "string") return value;
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    if (value && typeof value === "object") {
        const maybeMessage = (value as { message?: unknown }).message;
        if (typeof maybeMessage === "string") return maybeMessage;
        try {
            return JSON.stringify(value);
        } catch {
            return "Неизвестное предупреждение";
        }
    }
    return "";
};

const normalizeAlerts = (alerts: unknown): string[] => {
    if (!Array.isArray(alerts)) return [];
    return alerts
        .map((item) => toSafeText(item).trim())
        .filter(Boolean);
};

const isApiMessage = (value: unknown): value is ApiMessage => {
    if (!value || typeof value !== "object") return false;
    const candidate = value as ApiMessage;
    return Boolean(candidate.code && candidate.message !== undefined);
};

const isNewDashboardResponse = (
    payload: DashboardApiResponseNew | DashboardApiResponseOld,
): payload is DashboardApiResponseNew => {
    return "summary" in payload && "series" in payload;
};

export const getDashboardData = async (): Promise<DashboardData> => {
    const { data } = await api.get<unknown>("dashboard/");

    if (isApiMessage(data)) {
        throw new Error(toSafeText(data.message) || "Ошибка загрузки дашборда");
    }

    const typed = data as DashboardApiResponseNew | DashboardApiResponseOld;

    if (isNewDashboardResponse(typed)) {
        return {
            ...typed.summary,
            activity_7_days: Array.isArray(typed.series.activity_7_days) ? typed.series.activity_7_days : [],
            alerts: normalizeAlerts(typed.alerts),
            as_of: typed.meta?.as_of ?? new Date().toISOString().slice(0, 10),
            timezone: typed.meta?.timezone ?? "Asia/Tashkent",
        };
    }

    const old = typed as DashboardApiResponseOld;

    return {
        ...old,
        total_employees: Number(old.total_employees ?? 0),
        total_departments: Number(old.total_departments ?? 0),
        today_present: Number(old.today_present ?? 0),
        today_late: Number(old.today_late ?? 0),
        today_present_change_percent: Number(old.today_present_change_percent ?? 0),
        today_late_change_percent: Number(old.today_late_change_percent ?? 0),
        activity_7_days: Array.isArray(old.activity_7_days) ? old.activity_7_days : [],
        today_present_percent: old.total_employees
            ? Number(((Number(old.today_present ?? 0) / Number(old.total_employees ?? 0)) * 100).toFixed(1))
            : 0,
        today_late_percent: old.total_employees
            ? Number(((Number(old.today_late ?? 0) / Number(old.total_employees ?? 0)) * 100).toFixed(1))
            : 0,
        alerts: [],
        as_of: new Date().toISOString().slice(0, 10),
        timezone: "Asia/Tashkent",
    };
};
