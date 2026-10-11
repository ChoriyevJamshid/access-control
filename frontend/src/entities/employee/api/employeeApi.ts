import { api } from "@/shared/api/axios";
import type { Employee, CreateEmployeePayload } from "../types";

export const getEmployees = async (): Promise<Employee[]> => {
    const { data } = await api.get("employees/employees/");
    return data;
};

export const searchEmployees = async (query: string): Promise<Employee[]> => {
    const { data } = await api.post("employees/search/", { query });
    return data;
};

export const getEmployee = async (id: number): Promise<Employee> => {
    const { data } = await api.get(`employees/employees/${id}/`);
    return data;
};

export const createEmployee = async (payload: CreateEmployeePayload): Promise<Employee> => {
    const { data } = await api.post("employees/create/", payload);
    return data;
};

export const getEmployeeCompensation = async (employeeId: number) => {
    const { data } = await api.get(`employees/${employeeId}/compensation/`);
    return data;
};

export const updateEmployeeDetail = async ({
    id,
    payload,
}: {
    id: number;
    payload: Employee["detail"];
}) => {
    const { data } = await api.patch(`employees/employees/${id}/update/`, payload);
    return data;
};
