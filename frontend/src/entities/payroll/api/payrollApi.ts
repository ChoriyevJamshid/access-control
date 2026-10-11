import { api } from "@/shared/api/axios";
import type { CreatePayrollPeriodPayload, EmployeePayroll, PayrollPeriod } from "../types";

export const getPayrollPeriods = async (): Promise<PayrollPeriod[]> => {
    const { data } = await api.get("payroll-periods/");
    return data;
};

export const createPayrollPeriod = async (
    payload: CreatePayrollPeriodPayload,
): Promise<PayrollPeriod> => {
    const { data } = await api.post("payroll-periods/create/", payload);
    return data;
};

export const recalculatePayrollPeriod = async (periodId: number): Promise<{ detail: string }> => {
    const { data } = await api.post(`payroll-periods/${periodId}/recalculate/`);
    return data;
};

export const getEmployeePayrolls = async (periodId: number): Promise<EmployeePayroll[]> => {
    const { data } = await api.get(`payroll-periods/${periodId}/employees/`);
    return data;
};

export const getEmployeePayroll = async (payrollId: number): Promise<EmployeePayroll> => {
    const { data } = await api.get(`payroll-periods/employee-payrolls/${payrollId}/`);
    return data;
};

const getHeaderValue = (headers: unknown, key: string): string | null => {
    if (!headers || typeof headers !== "object") return null;

    const value = (headers as Record<string, unknown>)[key];
    return typeof value === "string" ? value : null;
};

const extractFilename = (contentDisposition: string | null): string => {
    if (!contentDisposition) return "attendance.xlsx";

    const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match?.[1]) {
        return decodeURIComponent(utf8Match[1]);
    }

    const basicMatch = contentDisposition.match(/filename="?([^"]+)"?/i);
    if (basicMatch?.[1]) {
        return basicMatch[1];
    }

    return "attendance.xlsx";
};

export const downloadPayrollAttendanceExcel = async (
    periodId: number,
): Promise<{ blob: Blob; filename: string }> => {
    const response = await api.get(`payroll-periods/${periodId}/attendance-excel/`, {
        responseType: "blob",
    });

    return {
        blob: response.data,
        filename: extractFilename(getHeaderValue(response.headers, "content-disposition")),
    };
};

export const finalizeEmployeePayroll = async (payrollId: number): Promise<{ detail: string }> => {
    const { data } = await api.post(`payroll-periods/employee-payrolls/${payrollId}/finalize/`);
    return data;
};

export const finalizeSelectedEmployeePayrolls = async (
    payrollIds: number[],
): Promise<{ detail: string }> => {
    const { data } = await api.post("payroll-periods/employee-payrolls/finalize/", {
        payroll_ids: payrollIds,
    });
    return data;
};
