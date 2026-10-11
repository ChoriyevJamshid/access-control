import { Layout, Menu, Avatar, Typography, Skeleton, Flex, Button, Tooltip } from "antd";
import {
    DashboardOutlined,
    DeploymentUnitOutlined,
    TeamOutlined,
    CalendarOutlined,
    WalletOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getEnterprise } from "@/entities/enterprise/api/enterpriseApi";
import { useThemeMode } from "@/app/providers/themeContext";

const { Sider } = Layout;
const { Text } = Typography;

const menuItems = [
    { key: "/", icon: <DashboardOutlined />, label: "Дашборд" },
    { key: "/structure", icon: <DeploymentUnitOutlined />, label: "Структура" },
    { key: "/employees", icon: <TeamOutlined />, label: "Сотрудники" },
    { key: "/attendance", icon: <CalendarOutlined />, label: "Посещаемость" },
    { key: "/payroll", icon: <WalletOutlined />, label: "Зарплата" },
];

interface SidebarProps {
    collapsed: boolean;
    onCollapse: (v: boolean) => void;
}

const Sidebar = ({ collapsed, onCollapse }: SidebarProps) => {
    const navigate = useNavigate();
    const location = useLocation();
    const { mode } = useThemeMode();

    const { data: enterprise, isLoading } = useQuery({
        queryKey: ["enterprise"],
        queryFn: getEnterprise,
    });

    const borderColor = mode === "dark" ? "rgba(255,255,255,0.07)" : "rgba(0,0,0,0.08)";
    const bg = mode === "dark" ? "#141414" : "#ffffff";
    const elevatedBg = mode === "dark" ? "#1d1d1d" : "#f4f6fa";

    return (
        <Sider
            width={240}
            collapsedWidth={72}
            collapsed={collapsed}
            style={{
                position: "sticky",
                top: 0,
                height: "100vh",
                overflow: "hidden",
                borderRight: `1px solid ${borderColor}`,
                background: bg,
                display: "flex",
                flexDirection: "column",
                transition: "width 0.25s cubic-bezier(0.4,0,0.2,1)",
            }}
        >
            {/* Шапка: логотип + кнопка сворачивания */}
            <Flex
                align="center"
                justify={collapsed ? "center" : "space-between"}
                style={{
                    padding: collapsed ? "18px 0" : "14px 16px 14px 20px",
                    borderBottom: `1px solid ${borderColor}`,
                    minHeight: 56,
                }}
            >
                {!collapsed && (
                    <Text strong style={{ color: "#3b82f6", fontSize: 13, letterSpacing: 1.5 }}>
                        ACCESS CONTROL
                    </Text>
                )}
                <Tooltip title={collapsed ? "Развернуть" : "Свернуть"} placement="right">
                    <Button
                        type="text"
                        size="small"
                        icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                        onClick={() => onCollapse(!collapsed)}
                        style={{ color: mode === "dark" ? "rgba(255,255,255,0.45)" : "rgba(0,0,0,0.45)" }}
                    />
                </Tooltip>
            </Flex>

            {/* Карточка компании */}
            {!collapsed && (
                <Flex
                    align="center"
                    gap={10}
                    style={{
                        margin: "12px 12px 4px",
                        padding: "10px 12px",
                        borderRadius: 10,
                        background: elevatedBg,
                    }}
                >
                    <Avatar size={34} style={{ backgroundColor: "#3b82f6", flexShrink: 0 }}>
                        {isLoading ? "…" : enterprise?.name?.charAt(0) ?? "E"}
                    </Avatar>
                    <Flex vertical style={{ minWidth: 0 }}>
                        {isLoading ? (
                            <Skeleton.Input size="small" active style={{ width: 100 }} />
                        ) : (
                            <>
                                <Text strong ellipsis style={{ fontSize: 13 }}>
                                    {enterprise?.name ?? "Enterprise"}
                                </Text>
                                <Text type="secondary" ellipsis style={{ fontSize: 11 }}>
                                    {enterprise?.code ?? "—"}
                                </Text>
                            </>
                        )}
                    </Flex>
                </Flex>
            )}

            {collapsed && (
                <Flex justify="center" style={{ padding: "12px 0 4px" }}>
                    <Avatar size={34} style={{ backgroundColor: "#3b82f6" }}>
                        {isLoading ? "…" : enterprise?.name?.charAt(0) ?? "E"}
                    </Avatar>
                </Flex>
            )}

            {/* Навигация */}
            <Menu
                mode="inline"
                selectedKeys={[location.pathname]}
                theme={mode}
                items={menuItems}
                inlineCollapsed={collapsed}
                onClick={({ key }) => navigate(key)}
                style={{ border: "none", background: "transparent", marginTop: 8, flex: 1 }}
            />
        </Sider>
    );
};

export default Sidebar;
