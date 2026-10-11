import { api } from "@/shared/api/axios";
import type { Enterprise, Department } from "@/entities/employee/types";

export const getEnterprise = async (): Promise<Enterprise> => {
    const { data } = await api.get("enterprise/enterprise/");
    return data;
};

export const getDepartments = async (): Promise<Department[]> => {
    const { data } = await api.get("enterprise/departments/");
    return data;
};
export const createDepartment = async (payload: { name: string; parent?: number | null }) => {
    const { data } = await api.post("enterprise/departments/create/", payload);
    return data;
};
