export interface PayrollPeriod {
    id: number;
    start_date: string;
    end_date: string;
    is_closed?: boolean;
    created?: string;
}

export interface CreatePayrollPeriodPayload {
    start_date: string;
    end_date: string;
}

export interface PayrollItem {
    id: number;
    type: "BASE" | "OVERTIME" | "PENALTY" | string;
    amount: string;
    description: string;
    created: string;
}

export interface EmployeePayroll {
    id: number;
    employee: number;
    employee_name: string;
    period: number;
    period_start: string;
    period_end: string;
    total_work_seconds: number;
    total_amount: string;
    is_finalized: boolean;
    calculated_at: string | null;
    items: PayrollItem[];
}
