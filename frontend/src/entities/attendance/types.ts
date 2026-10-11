// Типы на основе Django-моделей бэкенда

export interface AccessEvent {
    id: number;
    employee: number;
    timestamp: string;
    type: "entry" | "exit";
}

export interface WorkSession {
    id: number;
    employee: number;
    started: string;
    ended: string | null;
    duration_seconds: number | null;
    closed: boolean;
}

export interface DailyAttendance {
    employee: string;
    date: string;
    planned_seconds: number;
    work_seconds: number;
    late_seconds: number;
    early_leave_seconds: number;
}


