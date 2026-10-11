import { useMemo, useState } from "react";
import type { Key } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { DownloadOutlined } from "@ant-design/icons";
import {
    Alert,
    Button,
    Card,
    DatePicker,
    Descriptions,
    Drawer,
    Empty,
    Form,
    Select,
    message,
    Popconfirm,
    Space,
    Spin,
    Table,
    Tag,
    Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import dayjs from "dayjs";
import "dayjs/locale/ru";
import {
    createPayrollPeriod,
    downloadPayrollAttendanceExcel,
    finalizeEmployeePayroll,
    finalizeSelectedEmployeePayrolls,
    getEmployeePayroll,
    getEmployeePayrolls,
    getPayrollPeriods,
    recalculatePayrollPeriod,
} from "@/entities/payroll/api/payrollApi";
import type { EmployeePayroll, PayrollItem, PayrollPeriod } from "@/entities/payroll/types";

dayjs.locale("ru");

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

type PayrollBulkAction = "finalize-selected";

const formatMoney = (value: string): string => {
    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) {
        return value;
    }
    return new Intl.NumberFormat("ru-RU", {
        style: "currency",
        currency: "UZS",
        maximumFractionDigits: 2,
    }).format(numericValue);
};

const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}ч ${minutes}м`;
};

const getItemTagColor = (type: PayrollItem["type"]): string => {
    if (type === "BASE") return "blue";
    if (type === "OVERTIME") return "green";
    if (type === "PENALTY") return "red";
    return "default";
};

const getItemTypeLabel = (type: PayrollItem["type"]): string => {
    if (type === "BASE") return "Базовый";
    if (type === "OVERTIME") return "Сверхурочные";
    if (type === "PENALTY") return "Штраф";
    return type;
};

const downloadBlobFile = (blob: Blob, filename: string) => {
    const objectUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = objectUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();

    window.URL.revokeObjectURL(objectUrl);
};

const PayrollPage = () => {
    const queryClient = useQueryClient();
    const [form] = Form.useForm();
    const [selectedPeriodId, setSelectedPeriodId] = useState<number | null>(null);
    const [selectedPayrollId, setSelectedPayrollId] = useState<number | null>(null);
    const [selectedRowKeys, setSelectedRowKeys] = useState<Key[]>([]);
    const [selectedAction, setSelectedAction] = useState<PayrollBulkAction | undefined>(undefined);

    const { data: periods = [], isLoading: periodsLoading, error: periodsError } = useQuery({
        queryKey: ["payroll-periods"],
        queryFn: getPayrollPeriods,
    });

    const orderedPeriods = useMemo(
        () => [...periods].sort((a, b) => dayjs(b.start_date).valueOf() - dayjs(a.start_date).valueOf()),
        [periods],
    );

    const selectedPeriod = useMemo(
        () => orderedPeriods.find((period) => period.id === selectedPeriodId) ?? orderedPeriods[0] ?? null,
        [orderedPeriods, selectedPeriodId],
    );

    const currentPeriodId = selectedPeriod?.id ?? null;

    const {
        data: payrolls = [],
        isLoading: payrollsLoading,
        error: payrollsError,
        refetch: refetchPayrolls,
    } = useQuery({
        queryKey: ["payrolls", currentPeriodId],
        queryFn: () => getEmployeePayrolls(currentPeriodId as number),
        enabled: !!currentPeriodId,
    });

    const { data: payrollDetail, isLoading: payrollDetailLoading } = useQuery({
        queryKey: ["payroll-detail", selectedPayrollId],
        queryFn: () => getEmployeePayroll(selectedPayrollId as number),
        enabled: !!selectedPayrollId,
    });

    const createPeriodMutation = useMutation({
        mutationFn: createPayrollPeriod,
        onSuccess: (period) => {
            message.success("Расчётный период создан");
            queryClient.invalidateQueries({ queryKey: ["payroll-periods"] });
            setSelectedPeriodId(period.id);
            form.resetFields();
        },
    });

    const recalculateMutation = useMutation({
        mutationFn: recalculatePayrollPeriod,
        onSuccess: (res) => {
            message.success(res.detail || "Пересчет запущен");
            refetchPayrolls();
        },
    });

    const finalizeMutation = useMutation({
        mutationFn: finalizeEmployeePayroll,
        onSuccess: (res, payrollId) => {
            message.success(res.detail || "Начисление финализировано");
            queryClient.invalidateQueries({ queryKey: ["payrolls", currentPeriodId] });
            queryClient.invalidateQueries({ queryKey: ["payroll-detail", payrollId] });
        },
    });

    const finalizeSelectedMutation = useMutation({
        mutationFn: finalizeSelectedEmployeePayrolls,
        onSuccess: (res) => {
            message.success(res.detail || "Выбранные начисления финализированы");
            setSelectedRowKeys([]);
            setSelectedAction(undefined);
            queryClient.invalidateQueries({ queryKey: ["payrolls", currentPeriodId] });
            if (selectedPayrollId) {
                queryClient.invalidateQueries({ queryKey: ["payroll-detail", selectedPayrollId] });
            }
        },
    });

    const downloadAttendanceExcelMutation = useMutation({
        mutationFn: downloadPayrollAttendanceExcel,
        onSuccess: ({ blob, filename }) => {
            downloadBlobFile(blob, filename);
            message.success("Excel-файл успешно скачан");
        },
        onError: () => {
            message.error("Не удалось скачать Excel-файл");
        },
    });

    const selectedPayrollIds = useMemo(
        () => selectedRowKeys.map((id) => Number(id)).filter((id) => Number.isFinite(id)),
        [selectedRowKeys],
    );

    const selectedDraftCount = useMemo(
        () => payrolls.filter((payroll) => selectedPayrollIds.includes(payroll.id) && !payroll.is_finalized).length,
        [payrolls, selectedPayrollIds],
    );

    const hasFinalizedInSelection = useMemo(
        () => payrolls.some((payroll) => selectedPayrollIds.includes(payroll.id) && payroll.is_finalized),
        [payrolls, selectedPayrollIds],
    );

    const isGoDisabled =
        !selectedAction ||
        selectedPayrollIds.length === 0 ||
        selectedDraftCount === 0 ||
        finalizeSelectedMutation.isPending;

    const handleBulkGo = () => {
        if (selectedAction !== "finalize-selected") return;
        if (selectedDraftCount === 0) {
            message.warning("Нет черновых начислений для финализации");
            return;
        }

        const draftIds = payrolls
            .filter((payroll) => selectedPayrollIds.includes(payroll.id) && !payroll.is_finalized)
            .map((payroll) => payroll.id);

        finalizeSelectedMutation.mutate(draftIds);
    };

    const payrollColumns: ColumnsType<EmployeePayroll> = [
        {
            title: "Сотрудник",
            dataIndex: "employee_name",
            key: "employee_name",
        },
        {
            title: "Отработано",
            dataIndex: "total_work_seconds",
            key: "total_work_seconds",
            render: (value: number) => formatDuration(value),
        },
        {
            title: "Итого",
            dataIndex: "total_amount",
            key: "total_amount",
            render: (value: string) => <Text strong>{formatMoney(value)}</Text>,
        },
        {
            title: "Статус",
            dataIndex: "is_finalized",
            key: "is_finalized",
            render: (isFinalized: boolean) => (
                <Tag color={isFinalized ? "green" : "gold"}>
                    {isFinalized ? "Финализирован" : "Черновик"}
                </Tag>
            ),
        },
        {
            title: "Рассчитано",
            dataIndex: "calculated_at",
            key: "calculated_at",
            render: (value: string | null) => (value ? dayjs(value).format("DD.MM.YYYY HH:mm") : "-"),
        },
        {
            title: "Действия",
            key: "actions",
            render: (_, row) => (
                <Button size="small" onClick={() => setSelectedPayrollId(row.id)}>
                    Детали
                </Button>
            ),
        },
    ];

    const onCreatePeriod = (values: { range: [dayjs.Dayjs, dayjs.Dayjs] }) => {
        const [start, end] = values.range;
        createPeriodMutation.mutate({
            start_date: start.format("YYYY-MM-DD"),
            end_date: end.format("YYYY-MM-DD"),
        });
    };

    return (
        <Space orientation="vertical" size={16} style={{ width: "100%" }}>
            <div>
                <Title level={4} style={{ marginBottom: 8 }}>Зарплата</Title>
                <Text type="secondary">Управление периодами, расчетами и финализацией начислений.</Text>
            </div>

            <Card title="Создать расчётный период">
                <Form form={form} layout="inline" onFinish={onCreatePeriod}>
                    <Form.Item
                        name="range"
                        rules={[{ required: true, message: "Выберите диапазон дат" }]}
                    >
                        <RangePicker />
                    </Form.Item>
                    <Form.Item>
                        <Button type="primary" htmlType="submit" loading={createPeriodMutation.isPending}>
                            Создать период
                        </Button>
                    </Form.Item>
                </Form>
            </Card>

            <Card
                title="Периоды"
                extra={
                    <Button
                        onClick={() => {
                            queryClient.invalidateQueries({ queryKey: ["payroll-periods"] });
                            if (currentPeriodId) {
                                refetchPayrolls();
                            }
                        }}
                    >
                        Обновить
                    </Button>
                }
            >
                {periodsLoading ? (
                    <Spin />
                ) : periodsError ? (
                    <Alert type="error" message="Не удалось загрузить расчётные периоды" showIcon />
                ) : orderedPeriods.length === 0 ? (
                    <Empty description="Периоды пока не созданы" />
                ) : (
                    <Space wrap>
                        {orderedPeriods.map((period: PayrollPeriod) => {
                            const isActive = currentPeriodId === period.id;
                            return (
                                <Tag
                                    key={period.id}
                                    color={isActive ? "processing" : "default"}
                                    style={{ cursor: "pointer", padding: "6px 10px" }}
                                    onClick={() => {
                                        setSelectedPeriodId(period.id);
                                        setSelectedRowKeys([]);
                                        setSelectedAction(undefined);
                                    }}
                                >
                                    {dayjs(period.start_date).format("DD.MM.YYYY")} - {dayjs(period.end_date).format("DD.MM.YYYY")}
                                    {period.is_closed ? " (закрыт)" : ""}
                                </Tag>
                            );
                        })}
                    </Space>
                )}
            </Card>

            <Card
                title={
                    currentPeriodId
                        ? `Начисления за период #${currentPeriodId}`
                        : "Начисления по сотрудникам"
                }
                extra={
                    <Space wrap>
                        <Select<PayrollBulkAction>
                            allowClear
                            placeholder="Действие"
                            value={selectedAction}
                            style={{ width: 220 }}
                            onChange={(value) => setSelectedAction(value)}
                            options={[{ label: "Finalize selected payrolls", value: "finalize-selected" }]}
                        />
                        <Popconfirm
                            title={`Финализировать выбранные начисления (${selectedDraftCount})?`}
                            description={
                                hasFinalizedInSelection
                                    ? "Финализированные записи будут пропущены."
                                    : "Операция выполнится для выбранных черновиков."
                            }
                            onConfirm={handleBulkGo}
                            okButtonProps={{ loading: finalizeSelectedMutation.isPending }}
                            disabled={isGoDisabled}
                        >
                            <Button type="default" disabled={isGoDisabled} loading={finalizeSelectedMutation.isPending}>
                                GO
                            </Button>
                        </Popconfirm>

                        <Popconfirm
                            title="Запустить пересчет периода?"
                            description="Расчет будет выполняться в фоне."
                            onConfirm={() => currentPeriodId && recalculateMutation.mutate(currentPeriodId)}
                            okButtonProps={{ loading: recalculateMutation.isPending }}
                            disabled={!currentPeriodId}
                        >
                            <Button type="primary" disabled={!currentPeriodId} loading={recalculateMutation.isPending}>
                                Пересчитать период
                            </Button>
                        </Popconfirm>

                        <Button
                            icon={<DownloadOutlined />}
                            disabled={!currentPeriodId}
                            loading={downloadAttendanceExcelMutation.isPending}
                            onClick={() => currentPeriodId && downloadAttendanceExcelMutation.mutate(currentPeriodId)}
                        >
                            Скачать Excel
                        </Button>
                    </Space>
                }
            >
                {selectedPayrollIds.length > 0 && (
                    <Alert
                        type="info"
                        showIcon
                        style={{ marginBottom: 12 }}
                        message={`Выбрано: ${selectedPayrollIds.length}`}
                        description={`Готово к финализации: ${selectedDraftCount}${
                            hasFinalizedInSelection ? ". Уже финализированные будут пропущены." : ""
                        }`}
                    />
                )}

                {payrollsError ? (
                    <Alert type="error" message="Не удалось загрузить начисления сотрудников" showIcon />
                ) : (
                    <Table
                        rowSelection={{
                            selectedRowKeys,
                            onChange: (keys) => setSelectedRowKeys(keys),
                            getCheckboxProps: () => ({ disabled: finalizeSelectedMutation.isPending }),
                        }}
                        dataSource={payrolls}
                        columns={payrollColumns}
                        loading={payrollsLoading}
                        rowKey="id"
                        pagination={{ pageSize: 10, showSizeChanger: true }}
                        locale={{ emptyText: currentPeriodId ? "Нет начислений" : "Выберите период" }}
                    />
                )}
            </Card>

            <Drawer
                title={payrollDetail ? `Начисление: ${payrollDetail.employee_name}` : "Детали начисления"}
                open={!!selectedPayrollId}
                size={560}
                onClose={() => setSelectedPayrollId(null)}
            >
                {payrollDetailLoading ? (
                    <Spin />
                ) : !payrollDetail ? (
                    <Empty description="Нет данных" />
                ) : (
                    <Space orientation="vertical" size={16} style={{ width: "100%" }}>
                        <Descriptions column={1} bordered size="small">
                            <Descriptions.Item label="Период">
                                {dayjs(payrollDetail.period_start).format("DD.MM.YYYY")} - {dayjs(payrollDetail.period_end).format("DD.MM.YYYY")}
                            </Descriptions.Item>
                            <Descriptions.Item label="Отработано">
                                {formatDuration(payrollDetail.total_work_seconds)}
                            </Descriptions.Item>
                            <Descriptions.Item label="Сумма">
                                <Text strong>{formatMoney(payrollDetail.total_amount)}</Text>
                            </Descriptions.Item>
                            <Descriptions.Item label="Статус">
                                <Tag color={payrollDetail.is_finalized ? "green" : "gold"}>
                                    {payrollDetail.is_finalized ? "Финализирован" : "Черновик"}
                                </Tag>
                            </Descriptions.Item>
                        </Descriptions>

                        <Card size="small" title="Элементы начисления">
                            <Table
                                dataSource={payrollDetail.items}
                                rowKey="id"
                                size="small"
                                pagination={false}
                                columns={[
                                    {
                                        title: "Тип",
                                        dataIndex: "type",
                                        key: "type",
                                        render: (type: PayrollItem["type"]) => (
                                            <Tag color={getItemTagColor(type)}>{getItemTypeLabel(type)}</Tag>
                                        ),
                                    },
                                    {
                                        title: "Описание",
                                        dataIndex: "description",
                                        key: "description",
                                    },
                                    {
                                        title: "Сумма",
                                        dataIndex: "amount",
                                        key: "amount",
                                        render: (amount: string) => formatMoney(amount),
                                    },
                                ]}
                                locale={{ emptyText: "Элементы начисления отсутствуют" }}
                            />
                        </Card>

                        <Popconfirm
                            title="Финализировать начисление сотрудника?"
                            onConfirm={() => finalizeMutation.mutate(payrollDetail.id)}
                            okButtonProps={{ loading: finalizeMutation.isPending }}
                            disabled={payrollDetail.is_finalized}
                        >
                            <Button
                                type="primary"
                                block
                                disabled={payrollDetail.is_finalized}
                                loading={finalizeMutation.isPending}
                            >
                                {payrollDetail.is_finalized ? "Уже финализировано" : "Финализировать начисление"}
                            </Button>
                        </Popconfirm>
                    </Space>
                )}
            </Drawer>
        </Space>
    );
};

export default PayrollPage;
