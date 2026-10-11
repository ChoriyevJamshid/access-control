import { useQuery } from "@tanstack/react-query";
import type { ColumnsType } from "antd/es/table";
import { Tag, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import DataTable from "@/shared/ui/DataTable";
import { getEmployees } from "@/entities/employee/api/employeeApi";
import type { Employee } from "@/entities/employee/types";

const { Title } = Typography;

const columns: ColumnsType<Employee> = [
    {
        title: "Код",
        dataIndex: "code",
        key: "code",
        align: "center",
        render: (val) => <Tag>{val}</Tag>,
    },
    {
        title: "Имя",
        dataIndex: "first_name",
        key: "first_name",
    },
    {
        title: "Фамилия",
        dataIndex: "last_name",
        key: "last_name",
    },
    {
        title: "Отчество",
        dataIndex: "middle_name",
        key: "middle_name",
    },
    {
        title: "Отдел",
        dataIndex: "department",
        key: "department",
        align: "center",
        render: (dep) => dep ? (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                <Tag color="blue" style={{ margin: 0 }}>{dep.name}</Tag>
                {dep.parent && <span style={{ fontSize: 12, color: "#9ca3af" }}>{dep.parent}</span>}
            </div>
        ) : <span style={{ color: "#9ca3af" }}>—</span>,
    },
    {
        title: "Тип З/П",
        key: "salary_type",
        render: (_, record) => record.detail?.salary_type ?? "—",
    },
    {
        title: "Сумма",
        key: "amount",
        render: (_, record) => record.detail?.amount ?? "—",
    },
    {
        title: "Действует с",
        key: "effective_from",
        render: (_, record) => record.detail?.effective_from ?? "—",
    },
    {
        title: "Действует по",
        key: "effective_to",
        render: (_, record) => record.detail?.effective_to ?? "—",
    },
];

const EmployeesPage = () => {
    const navigate = useNavigate();
    const { data, isLoading } = useQuery({
        queryKey: ["employees"],
        queryFn: getEmployees,
    });

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>Сотрудники</Title>
            <DataTable
                rows={data}
                columns={columns}
                isLoading={isLoading}
                onAddClick={() => navigate('/employees/create')}
                addButtonLabel="Добавить сотрудника"
                onRowClick={(record) => navigate(`/employees/${record.id}`)}
            />
        </div>
    );
};

export default EmployeesPage;