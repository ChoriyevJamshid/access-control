import { useQuery } from "@tanstack/react-query";
import type { ColumnsType } from "antd/es/table";
import { Alert, Button, DatePicker, Input, Select, Space, Tag, Typography } from "antd";
import type { AxiosError } from "axios";
import dayjs from "dayjs";
import { useEffect, useMemo, useState } from "react";
import DataTable from "@/shared/ui/DataTable";
import { getDailyAttendances } from "@/entities/attendance/api/attendanceApi";
import type { DailyAttendance } from "@/entities/attendance/types";
import { getEmployees } from "@/entities/employee/api/employeeApi";

const { Title } = Typography;

const toSafeText = (value: unknown): string => {
    if (typeof value === "string") return value;
    if (typeof value === "number" || typeof value === "boolean") return String(value);

    if (value && typeof value === "object") {
        const maybeMessage = (value as { message?: unknown }).message;
        if (typeof maybeMessage === "string") return maybeMessage;
        try {
            return JSON.stringify(value);
        } catch {
            return "Неизвестная ошибка";
        }
    }

    return "—";
};

const formatEmployeeValue = (value: unknown) => {
    if (typeof value === "string") return value;
    if (!value || typeof value !== "object") return "—";

    const employee = value as {
        first_name?: string;
        last_name?: string;
        middle_name?: string;
        full_name?: string;
        message?: string;
    };

    if (employee.full_name) return employee.full_name;

    const fullName = [employee.last_name, employee.first_name, employee.middle_name]
        .filter(Boolean)
        .join(" ")
        .trim();

    if (fullName) return fullName;
    if (employee.message) return toSafeText(employee.message);
    return "—";
};

const formatSeconds = (seconds: number) => {
    if (!seconds) return "—";
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return `${h}ч ${m}м`;
};

const columns: ColumnsType<DailyAttendance> = [
    {
        title: "Сотрудник",
        dataIndex: "employee",
        key: "employee",
        align: "center",
        render: (val) => <span style={{ fontWeight: 500 }}>{formatEmployeeValue(val)}</span>,
    },
    {
        title: "Дата",
        dataIndex: "date",
        key: "date",
        align: "center",
        sorter: (a, b) => a.date.localeCompare(b.date),
    },
    {
        title: "По плану",
        dataIndex: "planned_seconds",
        key: "planned_seconds",
        align: "center",
        render: (val) => formatSeconds(val),
    },
    {
        title: "Отработано",
        dataIndex: "work_seconds",
        key: "work_seconds",
        align: "center",
        render: (val) => formatSeconds(val),
    },
    {
        title: "Опоздание",
        dataIndex: "late_seconds",
        key: "late_seconds",
        align: "center",
        render: (val) =>
            val > 0 ? <Tag color="error">{formatSeconds(val)}</Tag> : <span style={{ color: "#9ca3af" }}>—</span>,
    },
    {
        title: "Ранний уход",
        dataIndex: "early_leave_seconds",
        key: "early_leave_seconds",
        align: "center",
        render: (val) =>
            val > 0 ? <Tag color="warning">{formatSeconds(val)}</Tag> : <span style={{ color: "#9ca3af" }}>—</span>,
    },
];

const AttendancePage = () => {
    const [searchValue, setSearchValue] = useState("");
    const [debouncedSearch, setDebouncedSearch] = useState("");
    const [selectedEmployeeId, setSelectedEmployeeId] = useState<number | undefined>(undefined);
    const [selectedDate, setSelectedDate] = useState<string | undefined>(undefined);

    useEffect(() => {
        const timer = window.setTimeout(() => {
            setDebouncedSearch(searchValue.trim());
        }, 400);

        return () => window.clearTimeout(timer);
    }, [searchValue]);

    const filters = useMemo(
        () => ({
            employee: selectedEmployeeId,
            date: selectedDate,
            search: debouncedSearch || undefined,
        }),
        [selectedEmployeeId, selectedDate, debouncedSearch]
    );

    const { data, isLoading, isError, error } = useQuery({
        queryKey: ["daily-attendances", filters],
        queryFn: () => getDailyAttendances(filters),
    });

    const { data: employees, isLoading: isEmployeesLoading } = useQuery({
        queryKey: ["employees", "attendance-filter"],
        queryFn: getEmployees,
    });

    const employeeOptions = useMemo(
        () =>
            (employees ?? []).map((employee) => ({
                value: employee.id,
                label: `${employee.last_name} ${employee.first_name} ${employee.middle_name}`.trim(),
            })),
        [employees]
    );

    const resetFilters = () => {
        setSearchValue("");
        setSelectedEmployeeId(undefined);
        setSelectedDate(undefined);
    };

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>Посещаемость</Title>

            <Space wrap size={12} style={{ marginBottom: 16 }}>
                <Input.Search
                    allowClear
                    placeholder="Поиск по ФИО"
                    value={searchValue}
                    onChange={(event) => setSearchValue(event.target.value)}
                    style={{ width: 280 }}
                />

                <Select
                    allowClear
                    showSearch
                    placeholder="Сотрудник"
                    optionFilterProp="label"
                    loading={isEmployeesLoading}
                    value={selectedEmployeeId}
                    options={employeeOptions}
                    onChange={(value) => setSelectedEmployeeId(value)}
                    style={{ width: 280 }}
                />

                <DatePicker
                    allowClear
                    placeholder="Дата"
                    format="YYYY-MM-DD"
                    value={selectedDate ? dayjs(selectedDate) : null}
                    onChange={(value) => setSelectedDate(value ? value.format("YYYY-MM-DD") : undefined)}
                />

                <Button onClick={resetFilters}>Сбросить</Button>
            </Space>

            {isError && (
                <Alert
                    type="error"
                    showIcon
                    style={{ marginBottom: 16 }}
                    message="Не удалось загрузить посещаемость"
                    description={toSafeText((error as AxiosError<{ message?: unknown }>)?.response?.data?.message || error?.message)}
                />
            )}

            <DataTable
                rows={data ?? []}
                columns={columns}
                isLoading={isLoading}
                rowKey={(record) => `${record.employee}-${record.date}`}
            />
        </div>
    );
};

export default AttendancePage;
