import { useEffect } from "react";
import { Modal, Form, Select, DatePicker, InputNumber, Button, Typography, Space, Alert, TimePicker } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import dayjs from "dayjs";
import type { Dayjs } from "dayjs";
import type { EmployeeDetail } from "@/entities/employee/types";

const { Title } = Typography;

interface UpdateEmployeeDetailModalProps {
    open: boolean;
    onClose: () => void;
    onSubmit: (values: EmployeeDetail) => void;
    initialData?: EmployeeDetail | null;
    isLoading?: boolean;
    errorMsg?: string | null;
}

interface WorkDayFormValue {
    weekday: number;
    from_time?: Dayjs | null;
    to_time?: Dayjs | null;
    hours?: number | null;
}

interface UpdateEmployeeDetailFormValues {
    salary_type: EmployeeDetail["salary_type"];
    amount: number;
    effective_from?: Dayjs | null;
    effective_to?: Dayjs | null;
    work_days?: WorkDayFormValue[];
}

const UpdateEmployeeDetailModal = ({ open, onClose, onSubmit, initialData, isLoading, errorMsg }: UpdateEmployeeDetailModalProps) => {
    const [form] = Form.useForm<UpdateEmployeeDetailFormValues>();

    useEffect(() => {
        if (open && initialData) {
            form.setFieldsValue({
                salary_type: initialData.salary_type,
                amount: Number(initialData.amount),
                effective_from: dayjs(),
                effective_to: null,
                work_days: initialData.work_days?.map(wd => ({
                    weekday: wd.weekday,
                    from_time: dayjs(wd.from_time, "HH:mm:ss"),
                    to_time: dayjs(wd.to_time, "HH:mm:ss"),
                    hours: Number(wd.hours)
                })) || [{ weekday: 0, hours: 8 }]
            });
        }
    }, [open, initialData, form]);

    const handleFinish = (values: UpdateEmployeeDetailFormValues) => {
        const payload: EmployeeDetail = {
            id: initialData?.id ?? 0,
            employee: initialData?.employee ?? 0,
            salary_type: values.salary_type,
            amount: String(values.amount),
            effective_from: values.effective_from ? values.effective_from.format("YYYY-MM-DD") : dayjs().format("YYYY-MM-DD"),
            effective_to: values.effective_to ? values.effective_to.format("YYYY-MM-DD") : null,
            is_active: initialData?.is_active ?? true,
            work_days: (values.work_days || []).map((wd, index) => ({
                id: initialData?.work_days?.[index]?.id ?? index,
                detail: initialData?.id ?? 0,
                weekday: wd.weekday,
                from_time: wd.from_time ? wd.from_time.format("HH:mm:ss") : "09:00:00",
                to_time: wd.to_time ? wd.to_time.format("HH:mm:ss") : "18:00:00",
                hours: String(wd.hours),
            })),
        };
        onSubmit(payload);
    };

    return (
        <Modal
            title="Обновить компенсацию"
            open={open}
            onCancel={onClose}
            footer={null}
            width={700}
            destroyOnClose
        >
            {errorMsg && (
                <Alert
                    message="Ошибка обновления"
                    description={errorMsg}
                    type="error"
                    showIcon
                    style={{ marginBottom: 24 }}
                />
            )}
            <Form
                form={form}
                layout="vertical"
                onFinish={handleFinish}
            >
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
                                        <TimePicker placeholder="С" format="HH:mm:ss" style={{ width: 120 }} />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'to_time']}
                                        rules={[{ required: true, message: 'Укажите время' }]}
                                    >
                                        <TimePicker placeholder="По" format="HH:mm:ss" style={{ width: 120 }} />
                                    </Form.Item>
                                    <Form.Item
                                        {...restField}
                                        name={[name, 'hours']}
                                        rules={[{ required: true, message: 'Часы' }]}
                                    >
                                        <InputNumber placeholder="Часы" min={0} style={{ width: 100 }} />
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

                <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
                    <Button type="primary" htmlType="submit" loading={isLoading} block size="large">
                        Сохранить изменения
                    </Button>
                </Form.Item>
            </Form>
        </Modal>
    );
};

export default UpdateEmployeeDetailModal;
