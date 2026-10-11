import { useState } from "react";
import { Button, Form, Input, Alert, Typography, theme } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { login } from "@/entities/auth/api/login";
import { useNavigate } from "react-router-dom";

const { Title, Text } = Typography;

const LoginPage = () => {
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { token } = theme.useToken();

    const handleLogin = async (values: { username: string; password: string }) => {
        setError(null);
        setLoading(true);
        try {
            const data = await login(values.username, values.password);
            localStorage.setItem("access", data.access);
            localStorage.setItem("refresh", data.refresh);
            navigate("/");
        } catch {
            setError("Неверный логин или пароль");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                minHeight: "100vh",
                background: token.colorBgLayout,
            }}
        >
            <div
                style={{
                    width: 380,
                    padding: "40px 40px 32px",
                    borderRadius: token.borderRadiusLG,
                    background: token.colorBgElevated,
                    boxShadow: token.boxShadowSecondary,
                    border: `1px solid ${token.colorBorderSecondary}`,
                }}
            >
                <div style={{ textAlign: "center", marginBottom: 32 }}>
                    <div
                        style={{
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 56,
                            height: 56,
                            borderRadius: "50%",
                            background: token.colorPrimaryBg,
                            marginBottom: 16,
                        }}
                    >
                        <LockOutlined style={{ fontSize: 24, color: token.colorPrimary }} />
                    </div>
                    <Title level={3} style={{ margin: 0 }}>
                        Access Control
                    </Title>
                    <Text type="secondary" style={{ fontSize: 14 }}>
                        Войдите в свой аккаунт
                    </Text>
                </div>

                {error && (
                    <Alert
                        message={error}
                        type="error"
                        showIcon
                        style={{ marginBottom: 20 }}
                        closable
                        onClose={() => setError(null)}
                    />
                )}

                <Form layout="vertical" onFinish={handleLogin} size="large">
                    <Form.Item
                        name="username"
                        rules={[{ required: true, message: "Введите имя пользователя" }]}
                    >
                        <Input
                            prefix={<UserOutlined style={{ color: token.colorTextPlaceholder }} />}
                            placeholder="Имя пользователя"
                        />
                    </Form.Item>

                    <Form.Item
                        name="password"
                        rules={[{ required: true, message: "Введите пароль" }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined style={{ color: token.colorTextPlaceholder }} />}
                            placeholder="Пароль"
                        />
                    </Form.Item>

                    <Form.Item style={{ marginBottom: 0, marginTop: 8 }}>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                            block
                            style={{ height: 44, fontWeight: 600 }}
                        >
                            Войти
                        </Button>
                    </Form.Item>
                </Form>
            </div>
        </div>
    );
};

export default LoginPage;