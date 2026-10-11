import { useState } from "react";
import { Form, Input, Button, Card, Typography, message, Alert } from "antd";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { createDepartment } from "@/entities/enterprise/api/enterpriseApi";
import { getApiErrorMessage } from "@/shared/api/getApiErrorMessage";
import DepartmentSelectModal from "@/pages/CreateEmployeePage/DepartmentSelectModal";

const { Title } = Typography;

interface CreateDepartmentFormValues {
    name: string;
    parent?: number | null;
}

const CreateDepartmentPage = () => {
    const [form] = Form.useForm<CreateDepartmentFormValues>();
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [isDepartmentModalOpen, setIsDepartmentModalOpen] = useState(false);
    const [selectedParentName, setSelectedParentName] = useState<string>('');
    const [errorMsg, setErrorMsg] = useState<string | null>(null);

    const mutation = useMutation({
        mutationFn: createDepartment,
        onSuccess: () => {
            message.success("Подразделение успешно создано");
            setErrorMsg(null);
            queryClient.invalidateQueries({ queryKey: ["departments"] });
            navigate("/structure");
        },
        onError: (err: unknown) => {
            setErrorMsg(getApiErrorMessage(err, "Произошла непредвиденная ошибка"));
        },
    });

    const onFinish = (values: CreateDepartmentFormValues) => {
        const payload = {
            name: values.name,
            parent: values.parent || null,
        };
        mutation.mutate(payload);
    };

    return (
        <Card style={{ maxWidth: 600, margin: '0 auto', borderRadius: 12 }}>
            <Title level={4} style={{ marginBottom: 24 }}>Создание подразделения</Title>

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
            >
                <Form.Item
                    name="name"
                    label="Название подразделения"
                    rules={[{ required: true, message: 'Обязательное поле' }]}
                >
                    <Input placeholder="Например: IT Отдел" size="large" />
                </Form.Item>

                <Form.Item
                    name="parent"
                    label="Родительское подразделение (необязательно)"
                >
                    <Input
                        size="large"
                        readOnly
                        placeholder="Кликните чтобы выбрать"
                        value={selectedParentName || (form.getFieldValue('parent') ? `ID: ${form.getFieldValue('parent')}` : '')}
                        onClick={() => setIsDepartmentModalOpen(true)}
                        style={{ cursor: 'pointer' }}
                        allowClear
                        onChange={(e) => {
                            if (!e.target.value) {
                                form.setFieldsValue({ parent: null });
                                setSelectedParentName('');
                            }
                        }}
                    />
                </Form.Item>

                <Form.Item style={{ marginTop: 32, marginBottom: 0 }}>
                    <Button
                        type="primary"
                        htmlType="submit"
                        loading={mutation.isPending}
                        block
                        size="large"
                    >
                        Создать подразделение
                    </Button>
                </Form.Item>
            </Form>

            <DepartmentSelectModal
                open={isDepartmentModalOpen}
                onClose={() => setIsDepartmentModalOpen(false)}
                onSelect={(id) => {
                    form.setFieldsValue({ parent: id });
                    setSelectedParentName(`ID: ${id}`);
                    setIsDepartmentModalOpen(false);
                }}
            />
        </Card>
    );
};

export default CreateDepartmentPage;
