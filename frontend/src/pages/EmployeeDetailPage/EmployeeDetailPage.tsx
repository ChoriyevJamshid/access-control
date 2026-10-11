import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { Card, Row, Col, Descriptions, Tag, Typography, Spin, Alert, Space, Button, message } from "antd";
import { EditOutlined } from "@ant-design/icons";
import { getEmployee, updateEmployeeDetail } from "@/entities/employee/api/employeeApi";
import type { EmployeeDetail } from "@/entities/employee/types";
import { getApiErrorMessage } from "@/shared/api/getApiErrorMessage";
import DataTable from "@/shared/ui/DataTable";
import UpdateEmployeeDetailModal from "./UpdateEmployeeDetailModal";

const { Title } = Typography;
const EmployeeDetailPage = () => {
    const { id } = useParams<{ id: string }>();
    const employeeId = Number(id);
    const queryClient = useQueryClient();
    const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false);
    const [updateError, setUpdateError] = useState<string | null>(null);

    const { data: employee, isLoading: empLoading, error: empError } = useQuery({
        queryKey: ["employee", employeeId],
        queryFn: () => getEmployee(employeeId),
        enabled: !!employeeId,
    });



    const updateMutation = useMutation({
        mutationFn: (payload: EmployeeDetail) => updateEmployeeDetail({ id: employeeId, payload }),
        onSuccess: () => {
            message.success("Компенсация успешно обновлена");
            setUpdateError(null);
            queryClient.invalidateQueries({ queryKey: ["employee", employeeId] });
            setIsUpdateModalOpen(false);
        },
        onError: (err: unknown) => {
            setUpdateError(getApiErrorMessage(err, "Произошла непредвиденная ошибка"));
        },
    });

    const handleUpdateSubmit = (values: EmployeeDetail) => {
        updateMutation.mutate(values);
    };

    return (
        <div>
            {empLoading ? (
                <Spin tip="Загрузка данных сотрудника..." />
            ) : empError ? (
                <Alert title="Ошибка загрузки сотрудника" type="error" />
            ) : employee ? (
                <>
                    <Title level={4} style={{ marginBottom: 24 }}>
                        Сотрудник: {employee.last_name} {employee.first_name} {employee.middle_name}
                    </Title>

                    <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                        <Col xs={24} md={12}>
                            <Card title="Основная информация">
                                <Descriptions column={1} size="small" bordered>
                                    <Descriptions.Item label="ID">{employee.id}</Descriptions.Item>
                                    <Descriptions.Item label="Код">{employee.code}</Descriptions.Item>
                                    <Descriptions.Item label="Имя">{employee.first_name}</Descriptions.Item>
                                    <Descriptions.Item label="Фамилия">{employee.last_name}</Descriptions.Item>
                                    <Descriptions.Item label="Отчество">{employee.middle_name}</Descriptions.Item>
                                </Descriptions>
                            </Card>
                        </Col>

                        <Col xs={24} md={12}>
                            <Space orientation="vertical" style={{ width: "100%" }} size="middle">
                                <Card title="Отдел">
                                    {employee.department ? (
                                        <Descriptions column={1} size="small" bordered>
                                            <Descriptions.Item label="Название">
                                                <Tag color="blue">{employee.department.name}</Tag>
                                            </Descriptions.Item>
                                            <Descriptions.Item label="Код">{employee.department.code}</Descriptions.Item>
                                            {employee.department.parent && (
                                                <Descriptions.Item label="Родительский отдел">{employee.department.parent}</Descriptions.Item>
                                            )}
                                        </Descriptions>
                                    ) : (
                                        <Typography.Text type="secondary">Отдел не назначен</Typography.Text>
                                    )}
                                </Card>

                                <Card
                                    title="Компенсация"
                                    extra={
                                        <Button
                                            type="link"
                                            icon={<EditOutlined />}
                                            onClick={() => setIsUpdateModalOpen(true)}
                                        >
                                            Изменить
                                        </Button>
                                    }
                                >
                                    {employee.detail ? (
                                        <Descriptions column={1} size="small" bordered>
                                            <Descriptions.Item label="Тип">{employee.detail.salary_type}</Descriptions.Item>
                                            <Descriptions.Item label="Сумма">{employee.detail.amount}</Descriptions.Item>
                                            <Descriptions.Item label="Действует с">{employee.detail.effective_from}</Descriptions.Item>
                                            <Descriptions.Item label="Действует по">
                                                {employee.detail.effective_to ?? "Бессрочно"}
                                            </Descriptions.Item>
                                        </Descriptions>
                                    ) : (
                                        <Typography.Text type="secondary">Нет данных о компенсации</Typography.Text>
                                    )}
                                </Card>
                            </Space>
                        </Col>
                    </Row>

                    {employee.detail && employee.detail.work_days && employee.detail.work_days.length > 0 && (
                        <Card title="Рабочие дни" style={{ marginBottom: 24 }}>
                            <DataTable
                                rows={employee.detail.work_days}
                                columns={[
                                    {
                                        title: "День недели",
                                        dataIndex: "weekday",
                                        render: (val: number) => {
                                            const days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"];
                                            return days[val] || val;
                                        }
                                    },
                                    { title: "С", dataIndex: "from_time" },
                                    { title: "По", dataIndex: "to_time" },
                                    { title: "Часы", dataIndex: "hours" }
                                ]}
                                isLoading={false}
                            />
                        </Card>
                    )}
                </>
            ) : null}



            <UpdateEmployeeDetailModal
                open={isUpdateModalOpen}
                onClose={() => {
                    setIsUpdateModalOpen(false);
                    setUpdateError(null);
                }}
                onSubmit={handleUpdateSubmit}
                initialData={employee?.detail}
                isLoading={updateMutation.isPending}
                errorMsg={updateError}
            />
        </div>
    );
};

export default EmployeeDetailPage;
