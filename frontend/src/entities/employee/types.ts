// Типы на основе Django-моделей бэкенда

export interface Enterprise {
    id: number;
    name: string;
    code: string;
}

export interface Department {
    id: number;
    name: string;
    code: string;
    enterprise: number | null;
    parent: number | null;
    children?: Department[];
}

export interface EmployeeDepartment {
    id: number;
    name: string;
    code: string;
    parent: string | null;
}

export interface Employee {
    id: number;
    first_name: string;
    last_name: string;
    middle_name: string;
    code: string;
    department: EmployeeDepartment | null;
    detail: EmployeeDetail | null;
}

export interface EmployeeDetail {
    id: number;
    employee: number;
    salary_type: "hourly" | "monthly" | "daily";
    amount: string;
    effective_from: string;
    effective_to: string | null;
    is_active: boolean;
    work_days?: EmployeeWorkDay[];
}

export interface EmployeeWorkDay {
    id: number;
    detail: number;
    weekday: number; // 0=Пн, 6=Вс
    from_time: string;
    to_time: string;
    hours: string;
}

export interface CreateEmployeePayload {
    department: number;
    first_name: string;
    last_name: string;
    middle_name: string;
    code: string;
    detail: {
        salary_type: "hourly" | "monthly" | "daily";
        amount: string;
        effective_from: string;
        effective_to: string;
        is_active: boolean;
        work_days: {
            weekday: number;
            from_time: string;
            to_time: string;
            hours: string;
        }[];
    };
}
