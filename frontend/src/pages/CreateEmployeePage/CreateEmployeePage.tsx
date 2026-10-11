import { useState } from "react";
import { Form, Input, Button, Card, Select, Switch, Space, DatePicker, TimePicker, InputNumber, Typography, message, Alert } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";
import { createEmployee } from "@/entities/employee/api/employeeApi";
import type { CreateEmployeePayload } from "@/entities/employee/types";
import { getApiErrorMessage } from "@/shared/api/getApiErrorMessage";
import DepartmentSelectModal from "./DepartmentSelectModal";

const { Title } = Typography;

interface WorkDayFormValue {
    weekday: number;
    from_time?: Dayjs | null;
    to_time?: Dayjs | null;
    hours?: number | null;
}

interface CreateEmployeeFormValues {
    department?: number;
    first_name: string;
    last_name: string;
    middle_name?: string;
    code?: string;
    salary_type?: "hourly" | "daily" | "monthly";
    amount?: number;
    effective_from?: Dayjs | null;
    effective_to?: Dayjs | null;
    is_active?: boolean;
    work_days?: WorkDayFormValue[];
}

const CreateEmployeePage = () => {
    const [form] = Form.useForm<CreateEmployeeFormValues>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isDepartmentModalOpen, setIsDepartmentModalOpen] = useState(false);
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: createEmployee,
        onSuccess: () => {
            message.success("Сотрудник успешно создан");
            setErrorMsg(null);
            queryClient.invalidateQueries({ queryKey: ["employees"] });
            navigate("/employees");
        },
        onError: (err: unknown) => {
            setErrorMsg(getApiErrorMessage(err, "Произошла непредвиденная ошибка"));
        },
    });

    const onFinish = (values: CreateEmployeeFormValues) => {
        const payload: CreateEmployeePayload = {
            department: values.department || 0,
            first_name: values.first_name,
            last_name: values.last_name,
            middle_name: values.middle_name || "",
            code: values.code || "",
            detail: {
                salary_type: values.salary_type || "hourly",
                amount: String(values.amount || "0"),
                effective_from: values.effective_from ? values.effective_from.format("YYYY-MM-DD") : dayjs().format("YYYY-MM-DD"),
                effective_to: values.effective_to ? values.effective_to.format("YYYY-MM-DD") : dayjs().format("YYYY-MM-DD"),
                is_active: values.is_active ?? true,
                work_days: (values.work_days || []).map((wd) => ({
                    weekday: wd.weekday,
                    from_time: wd.from_time ? wd.from_time.format("HH:mm:ss") : "09:00:00",
                    to_time: wd.to_time ? wd.to_time.format("HH:mm:ss") : "18:00:00",
                    hours: String(wd.hours || "8"),
                })),
            },
        };

        mutation.mutate(payload);
    };

    return (
        <Card style={{ maxWidth: 800, margin: '0 auto', borderRadius: 12 }}>
            <Title level={4} style={{ marginBottom: 24 }}>Создание сотрудника</Title>

            {errorMsg && (
                <Alert
                    message="Ошибка создания"
                    description={errorMsg}
                    type="error"
                    showIcon
                    style={{ marginBottom: 24 }}
                    closable
                    onClose={() => setErrorMsg(null)}
                />
            )}

            <Form
                form={form}
                layout="vertical"
                onFinish={onFinish}
                initialValues={{
                    is_active: true,
                    salary_type: 'hourly',
                    amount: 0,
                    work_days: [{ weekday: 0, hours: 8 }]
                }}
            >
                <Title level={5}>Основная информация</Title>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
                    <Form.Item name="first_name" label="Имя" rules={[{ required: true, message: 'Обязательное поле' }]}>
                        <Input placeholder="Иван" />
                    </Form.Item>
                    <Form.Item name="last_name" label="Фамилия" rules={[{ required: true, message: 'Обязательное поле' }]}>
                        <Input placeholder="Иванов" />
                    </Form.Item>
                    <Form.Item name="middle_name" label="Отчество">
                        <Input placeholder="Иванович" />
                    </Form.Item>
                    <Form.Item name="code" label="Код">
                        <Input placeholder="Код сотрудника" />
                    </Form.Item>
                    <Form.Item name="department" label="ID Отдела" rules={[{ required: true, message: 'Обязательное поле' }]}>
                        <InputNumber
                            style={{ width: '100%', cursor: 'pointer' }}
                            placeholder="Выберите отдел"
                            readOnly
                            onClick={() => setIsDepartmentModalOpen(true)}
                        />
                    </Form.Item>
                </div>

                <Title level={5} style={{ marginTop: 24 }}>Детали зарплаты</Title>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0 16px' }}>
                    <Form.Item name="salary_type" label="Тип З/П" rules={[{ required: true }]}>
                        <Select
                            options={[
                                { value: 'hourly', label: 'Почасовая' },
                                { value: 'daily', label: 'Дневная' },
                                { value: 'monthly', label: 'Ежемесячная' },
                            ]}
                        />
                    </Form.Item>
                    <Form.Item name="amount" label="Сумма" rules={[{ required: true }]}>
                        <InputNumber style={{ width: '100%' }} min={0} />
                    </Form.Item>
                    <Form.Item name="effective_from" label="Действует с">
                        <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
                    </Form.Item>
                    <Form.Item name="effective_to" label="Действует по">
                        <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
                    </Form.Item>
                    <Form.Item name="is_active" label="Активен" valuePropName="checked">
                        <Switch />
                    </Form.Item>
                </div>

                <Title level={5} style={{ marginTop: 24 }}>Рабочие дни</Title>
                <Form.List name="work_days">
                    {(fields, { add, remove }) => (
                        <>
                            {fields.map(({ key, name, ...restField }) => (
                                <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline" wrap>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'weekday']}
                                        rules={[{ required: true, message: 'Укажите день' }]}
                                    >
                                        <Select style={{ width: 140 }} placeholder="День недели">
                                            <Select.Option value={0}>Понедельник</Select.Option>
                                            <Select.Option value={1}>Вторник</Select.Option>
                                            <Select.Option value={2}>Среда</Select.Option>
                                            <Select.Option value={3}>Четверг</Select.Option>
                                            <Select.Option value={4}>Пятница</Select.Option>
                                            <Select.Option value={5}>Суббота</Select.Option>
                                            <Select.Option value={6}>Воскресенье</Select.Option>
                                        </Select>
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'from_time']}
                                        rules={[{ required: true, message: 'Укажите время' }]}
                                    >
                                        <TimePicker placeholder="С" format="HH:mm:ss" />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'to_time']}
                                        rules={[{ required: true, message: 'Укажите время' }]}
                                    >
                                        <TimePicker placeholder="По" format="HH:mm:ss" />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'hours']}
                                        rules={[{ required: true, message: 'Часы' }]}
                                    >
                                        <InputNumber placeholder="Часы" min={0} />
                                    </Form.Item>
                                    <MinusCircleOutlined onClick={() => remove(name)} style={{ color: 'red' }} />
                                </Space>
                            ))}
                            <Form.Item>
                                <Button type="dashed" onClick={() => add()} block icon={<PlusOutlined />}>
                                    Добавить рабочий день
                                </Button>
                            </Form.Item>
                        </>
                    )}
                </Form.List>

                <Form.Item style={{ marginTop: 24 }}>
                    <Button type="primary" htmlType="submit" loading={mutation.isPending} block size="large">
                        Создать сотрудника
                    </Button>
                </Form.Item>
            </Form>

            <DepartmentSelectModal
                open={isDepartmentModalOpen}
                onClose={() => setIsDepartmentModalOpen(false)}
                onSelect={(id) => {
                    form.setFieldsValue({ department: id });
                    setIsDepartmentModalOpen(false);
                }}
            />
        </Card>
    );
};

export default CreateEmployeePage;
