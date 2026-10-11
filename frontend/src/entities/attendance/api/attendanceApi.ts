import { api } from "@/shared/api/axios";
import type { AccessEvent, DailyAttendance, WorkSession } from "../types";

export interface DailyAttendanceFilters {
    employee?: number;
    date?: string;
    search?: string;
}

type AttendanceApiMessage = {
    level?: string;
    code?: string;
    message?: unknown;
};

type AttendanceApiEmployee =
    | string
    | {
        first_name?: string;
        last_name?: string;
        middle_name?: string;
        full_name?: string;
        message?: never;
    }
    | AttendanceApiMessage;

type AttendanceApiRow = {
    employee?: AttendanceApiEmployee;
    date?: string;
    planned_seconds?: number;
    work_seconds?: number;
    late_seconds?: number;
    early_leave_seconds?: number;
};

const normalizeEmployee = (employee: AttendanceApiEmployee): string => {
    const safeText = (value: unknown): string => {
        if (typeof value === "string") return value;
        if (typeof value === "number" || typeof value === "boolean") return String(value);
        if (value && typeof value === "object") {
            const maybeMessage = (value as { message?: unknown }).message;
            if (typeof maybeMessage === "string") return maybeMessage;
            try {
                return JSON.stringify(value);
            } catch {
                return "—";
            }
        }
        return "—";
    };

    if (!employee) return "—";

    if (typeof employee === "string") {
        return employee;
    }

    if ("full_name" in employee && employee.full_name) {
        return employee.full_name;
    }

    if ("message" in employee && employee.message) {
        return safeText(employee.message);
    }

    const fullName = [
        "last_name" in employee ? employee.last_name : undefined,
        "first_name" in employee ? employee.first_name : undefined,
        "middle_name" in employee ? employee.middle_name : undefined,
    ].filter(Boolean).join(" ").trim();

    if (fullName) {
        return fullName;
    }

    return "—";
};

const normalizeAttendanceRow = (row: AttendanceApiRow): DailyAttendance => ({
    employee: normalizeEmployee(row.employee as AttendanceApiEmployee),
    date: row.date ?? "",
    planned_seconds: Number(row.planned_seconds ?? 0),
    work_seconds: Number(row.work_seconds ?? 0),
    late_seconds: Number(row.late_seconds ?? 0),
    early_leave_seconds: Number(row.early_leave_seconds ?? 0),
});

const isApiMessage = (value: unknown): value is AttendanceApiMessage => {
    if (!value || typeof value !== "object") return false;
    const message = value as AttendanceApiMessage;
    return Boolean(message.message && message.code);
};

export const getDailyAttendances = async (
    filters?: DailyAttendanceFilters
): Promise<DailyAttendance[]> => {
    const { data } = await api.get<unknown>("access-controls/daily-attendances/", {
        params: filters,
    });

    if (Array.isArray(data)) {
        return data.map((row) => normalizeAttendanceRow(row as AttendanceApiRow));
    }

    const maybePaginated = data as { results?: unknown };
    if (Array.isArray(maybePaginated?.results)) {
        return maybePaginated.results.map((row) => normalizeAttendanceRow(row as AttendanceApiRow));
    }

    if (isApiMessage(data)) {
        const message = typeof data.message === "string" ? data.message : "Ошибка загрузки посещаемости";
        throw new Error(message);
    }

    return [];
};

export const getWorkSessions = async (): Promise<WorkSession[]> => {
    const { data } = await api.get("access-controls/work-sessions/");
    return data;
};

export const createAccessEvent = async (
    payload: Pick<AccessEvent, "employee" | "timestamp" | "type">
): Promise<AccessEvent> => {
    const { data } = await api.post("access-controls/create/", payload);
    return data;
};
