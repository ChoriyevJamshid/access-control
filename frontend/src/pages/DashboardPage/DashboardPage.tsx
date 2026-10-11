import { Alert, Card, Col, Progress, Row, Space, Spin, Tag, Typography, theme } from "antd";
import {
    ApartmentOutlined,
    CalendarOutlined,
    TeamOutlined,
    CheckCircleOutlined,
    ClockCircleOutlined,
    ArrowUpOutlined,
    ArrowDownOutlined,
    WarningOutlined,
} from "@ant-design/icons";
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { getDashboardData } from "@/entities/dashboard/api/dashboardApi";
import dayjs from "dayjs";
import "dayjs/locale/ru";

dayjs.locale("ru");

const { Title, Text } = Typography;

const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}ч ${minutes}м`;
};

const formatMinutes = (seconds: number): string => {
    return `${Math.round(seconds / 60)} мин`;
};

const formatTrend = (value: number) => `${value > 0 ? "+" : ""}${value}%`;

const renderTrendIcon = (isPositive: boolean) => {
    return isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />;
};

const toSafeText = (value: unknown): string => {
    if (typeof value === "string") return value;
    if (typeof value === "number" || typeof value === "boolean") return String(value);

    if (value && typeof value === "object") {
        const maybeMessage = (value as { message?: unknown }).message;
        if (typeof maybeMessage === "string") return maybeMessage;
        try {
            return JSON.stringify(value);
        } catch {
            return "Неизвестное предупреждение";
        }
    }

    return "";
};

const DashboardPage = () => {
    const { token } = theme.useToken();

    const { data, isLoading, isError } = useQuery({
        queryKey: ["dashboard"],
        queryFn: getDashboardData,
    });

    if (isLoading) {
        return (
            <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100%", minHeight: 400 }}>
                <Spin size="large" />
            </div>
        );
    }

    if (isError || !data) {
        return (
            <div style={{ padding: 24, textAlign: "center" }}>
                <Text type="danger">Ошибка при загрузке данных дашборда</Text>
            </div>
        );
    }

    const {
        total_employees,
        total_departments,
        today_present,
        today_present_percent,
        today_present_change_percent,
        today_late,
        today_late_percent,
        today_late_change_percent,
        activity_7_days,
        alerts,
        as_of,
        timezone,
    } = data;

    const stats = [
        {
            title: "Всего сотрудников",
            value: total_employees,
            icon: <TeamOutlined />,
        },
        {
            title: "Сегодня в офисе",
            value: today_present,
            icon: <CheckCircleOutlined />,
            trend: formatTrend(today_present_change_percent),
            positive: today_present_change_percent >= 0,
            caption: `${today_present_percent}% от штата`,
        },
        {
            title: "Опоздания",
            value: today_late,
            icon: <WarningOutlined />,
            trend: formatTrend(today_late_change_percent),
            positive: today_late_change_percent <= 0,
            caption: `${today_late_percent}% от штата`,
        },
        {
            title: "Отделы",
            value: total_departments,
            icon: <ApartmentOutlined />,
        },
    ];

    const chartData = activity_7_days.map((day) => ({
        name: dayjs(day.date).format("dd"),
        value: day.present_count,
        fullDate: day.date,
        workHours: Number((day.total_work_seconds / 3600).toFixed(1)),
        lateMinutes: Number((day.total_late_seconds / 60).toFixed(0)),
        totalWorkSeconds: day.total_work_seconds,
        totalLateSeconds: day.total_late_seconds,
    }));

    const totalWorkSecondsWeek = activity_7_days.reduce((acc, day) => acc + day.total_work_seconds, 0);
    const totalLateSecondsWeek = activity_7_days.reduce((acc, day) => acc + day.total_late_seconds, 0);
    const avgPresentCount =
        activity_7_days.length > 0
            ? Number(
                (
                    activity_7_days.reduce((acc, day) => acc + day.present_count, 0) /
                    activity_7_days.length
                ).toFixed(1),
            )
            : 0;

    return (
        <div>
            <Card
                style={{
                    marginBottom: 16,
                    border: "none",
                    overflow: "hidden",
                    background: `linear-gradient(120deg, ${token.colorPrimaryBg} 0%, ${token.colorBgElevated} 65%)`,
                }}
            >
                <Space direction="vertical" size={4} style={{ width: "100%" }}>
                    <Title level={4} style={{ margin: 0 }}>Обзор компании</Title>
                    <Text type="secondary">
                        Актуально на {dayjs(as_of).format("D MMMM YYYY")} ({timezone})
                    </Text>
                    <Space wrap style={{ marginTop: 8 }}>
                        <Tag icon={<CalendarOutlined />} color="processing">7-дневная аналитика</Tag>
                        <Tag icon={<ClockCircleOutlined />} color="default">
                            Средняя явка: {avgPresentCount} чел./день
                        </Tag>
                    </Space>
                </Space>
            </Card>

            <Row gutter={[16, 16]}>
                {stats.map((s) => (
                    <Col key={s.title} xs={24} sm={12} md={6}>
                        <Card
                            style={{
                                border: `1px solid ${token.colorBorderSecondary}`,
                                boxShadow: token.boxShadowSecondary,
                            }}
                        >
                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                <div>
                                    <Text type="secondary" style={{ fontSize: 12 }}>{s.title}</Text>
                                    <Title level={2} style={{ margin: "4px 0 0" }}>{s.value}</Title>
                                    {s.caption && (
                                        <Text type="secondary" style={{ fontSize: 12 }}>{s.caption}</Text>
                                    )}
                                    {s.trend && (
                                        <Text
                                            style={{
                                                fontSize: 12,
                                                color: s.positive ? token.colorSuccess : token.colorError,
                                            }}
                                        >
                                            {renderTrendIcon(s.positive)}
                                            {" "}{s.trend}
                                        </Text>
                                    )}
                                </div>
                                <div style={{
                                    fontSize: 24,
                                    color: token.colorPrimary,
                                    opacity: 0.7,
                                    paddingTop: 6,
                                }}>
                                    {s.icon}
                                </div>
                            </div>
                        </Card>
                    </Col>
                ))}
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 8 }}>
                <Col xs={24} lg={16}>
                    <Card>
                        <Title level={5} style={{ marginBottom: 16 }}>Посещаемость за 7 дней</Title>
                        <ResponsiveContainer width="100%" height={320}>
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="attendance-grad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={token.colorPrimary} stopOpacity={0.28} />
                                        <stop offset="95%" stopColor={token.colorPrimary} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke={token.colorBorderSecondary} vertical={false} />
                                <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis allowDecimals={false} fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    labelFormatter={(label, payload) => payload?.[0]?.payload?.fullDate || label}
                                    formatter={(value) => [`${Number(value ?? 0)} чел.`, "Присутствовало"]}
                                    contentStyle={{
                                        borderRadius: 10,
                                        border: `1px solid ${token.colorBorder}`,
                                        background: token.colorBgElevated,
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    name="Присутствовало"
                                    stroke={token.colorPrimary}
                                    strokeWidth={3}
                                    fill="url(#attendance-grad)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </Card>
                </Col>

                <Col xs={24} lg={8}>
                    <Card style={{ marginBottom: 16 }}>
                        <Title level={5} style={{ marginBottom: 20 }}>Пульс дня</Title>
                        <Row gutter={12}>
                            <Col span={12} style={{ textAlign: "center" }}>
                                <Progress type="dashboard" percent={today_present_percent} strokeColor={token.colorSuccess} size={128} />
                                <Text strong>Присутствуют</Text>
                            </Col>
                            <Col span={12} style={{ textAlign: "center" }}>
                                <Progress type="dashboard" percent={today_late_percent} strokeColor={token.colorWarning} size={128} />
                                <Text strong>Опаздывают</Text>
                            </Col>
                        </Row>
                    </Card>

                    {alerts.length > 0 ? (
                        <Space direction="vertical" style={{ width: "100%" }}>
                            {alerts.map((item, index) => (
                                <Alert key={`${index}-${toSafeText(item)}`} message={toSafeText(item)} type="warning" showIcon />
                            ))}
                        </Space>
                    ) : (
                        <Alert
                            type="success"
                            showIcon
                            message="Критичных предупреждений нет"
                            description="Сегодня показатели в норме, система работает стабильно."
                        />
                    )}
                </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 8 }}>
                <Col xs={24}>
                    <Card>
                        <Title level={5} style={{ marginBottom: 16 }}>Рабочие часы и опоздания</Title>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke={token.colorBorderSecondary} vertical={false} />
                                <XAxis dataKey="name" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="left" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="right" orientation="right" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    labelFormatter={(label, payload) => payload?.[0]?.payload?.fullDate || label}
                                    formatter={(value, name) => {
                                        const safeValue = Number(value ?? 0);
                                        if (name === "Часы") {
                                            return [`${safeValue} ч`, name];
                                        }
                                        return [`${safeValue} мин`, name];
                                    }}
                                    contentStyle={{
                                        borderRadius: 10,
                                        border: `1px solid ${token.colorBorder}`,
                                        background: token.colorBgElevated,
                                    }}
                                />
                                <Bar yAxisId="left" dataKey="workHours" name="Часы" fill={token.colorPrimary} radius={[6, 6, 0, 0]} />
                                <Bar yAxisId="right" dataKey="lateMinutes" name="Опоздания" fill={token.colorWarning} radius={[6, 6, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                        <Row gutter={16} style={{ marginTop: 8 }}>
                            <Col xs={24} md={12}>
                                <Text type="secondary">Итого рабочих часов за неделю:</Text>
                                <Title level={5} style={{ marginTop: 4 }}>{formatDuration(totalWorkSecondsWeek)}</Title>
                            </Col>
                            <Col xs={24} md={12}>
                                <Text type="secondary">Суммарные опоздания за неделю:</Text>
                                <Title level={5} style={{ marginTop: 4 }}>{formatMinutes(totalLateSecondsWeek)}</Title>
                            </Col>
                        </Row>
                    </Card>
                </Col>
            </Row>
        </div>
    );
};

export default DashboardPage;