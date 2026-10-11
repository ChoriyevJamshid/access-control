import { useQuery } from "@tanstack/react-query";
import type { ColumnsType } from "antd/es/table";
import { Tag, Space, Typography } from "antd";
import { useNavigate } from "react-router-dom";
import DataTable from "@/shared/ui/DataTable";
import { getDepartments } from "@/entities/enterprise/api/enterpriseApi";
import type { Department } from "@/entities/employee/types";

const { Title } = Typography;

const columns: ColumnsType<Department> = [
    { title: "Название", dataIndex: "name", key: "name" },
    {
        title: "Код",
        dataIndex: "code",
        key: "code",
        align: "center",
        render: (val) => <Tag>{val}</Tag>,
    },
    {
        title: "Подотделы",
        dataIndex: "children",
        key: "children",
        render: (children: Department[]) =>
            children?.length ? (
                <Space wrap>
                    {children.map((c) => (
                        <Tag key={c.id} color="geekblue">{c.name}</Tag>
                    ))}
                </Space>
            ) : (
                <span style={{ color: "#9ca3af" }}>—</span>
            ),
    },
];

const DepartmentsPage = () => {
    const navigate = useNavigate();
    const { data, isLoading } = useQuery({
        queryKey: ["departments"],
        queryFn: getDepartments,
    });

    return (
        <div>
            <Title level={4} style={{ marginBottom: 16 }}>Отделы</Title>
            <DataTable
                rows={data}
                columns={columns}
                isLoading={isLoading}
                onAddClick={() => navigate("/departments/create")}
                addButtonLabel="Новый отдел"
            />
        </div>
    );
};

export default DepartmentsPage;
