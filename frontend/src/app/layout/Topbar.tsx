import { Layout, Button, Space, Badge, Tooltip, Typography, theme, Divider } from "antd";
import {
    LogoutOutlined,
    BellOutlined,
    SunOutlined,
    MoonOutlined,
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useThemeMode } from "@/app/providers/themeContext";

const { Header } = Layout;
const { Text } = Typography;

const pageTitles: Record<string, string> = {
    "/": "Дашборд",
    "/employees": "Сотрудники",
    "/attendance": "Посещаемость",
    "/departments": "Отделы",
    "/structure": "Структура подразделений",
    "/employees/create": "Создание сотрудника",
    "/departments/create": "Создание подразделения",
    "/payroll": "Зарплата",
    "/employees/:id": "Профиль сотрудника",
};

const Topbar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const { mode, toggleMode } = useThemeMode();
    const { token } = theme.useToken();

    const handleLogout = () => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        navigate("/login");
    };

    const rawTitle = Object.entries(pageTitles).find(([path]) =>
        location.pathname === path || location.pathname.startsWith(path + "/")
    )?.[1] ?? "Access Control";

    return (
        <Header
            style={{
                display: "flex",
                alignItems: "center",
                padding: "0 24px",
                borderBottom: mode === "dark"
                    ? "1px solid rgba(255,255,255,0.07)"
                    : "1px solid rgba(0,0,0,0.08)",
                height: 56,
                position: "sticky",
                top: 0,
                zIndex: 100,
                boxShadow: mode === "dark"
                    ? "0 1px 0 rgba(255,255,255,0.04)"
                    : "0 1px 3px rgba(0,0,0,0.05)",
            }}
        >
            <Text strong style={{ flex: 1, fontSize: 16, color: token.colorText }}>
                {rawTitle}
            </Text>

            <Space size={2} align="center">
                <Tooltip title="Уведомления">
                    <Badge count={0} size="small">
                        <Button
                            type="text"
                            shape="circle"
                            icon={<BellOutlined style={{ fontSize: 17 }} />}
                        />
                    </Badge>
                </Tooltip>

                <Divider orientation="vertical" style={{ height: 20, margin: "0 4px" }} />

                <Tooltip title={mode === "dark" ? "Светлая тема" : "Тёмная тема"}>
                    <Button
                        type="text"
                        shape="circle"
                        icon={mode === "dark"
                            ? <SunOutlined style={{ fontSize: 17 }} />
                            : <MoonOutlined style={{ fontSize: 17 }} />
                        }
                        onClick={toggleMode}
                    />
                </Tooltip>

                <Divider orientation="vertical" style={{ height: 20, margin: "0 4px" }} />

                <Tooltip title="Выйти">
                    <Button
                        type="text"
                        shape="circle"
                        danger
                        icon={<LogoutOutlined style={{ fontSize: 17 }} />}
                        onClick={handleLogout}
                    />
                </Tooltip>
            </Space>
        </Header>
    );
};

export default Topbar;
