import { Card, Typography, theme } from "antd";
import { ArrowUpOutlined, ArrowDownOutlined } from "@ant-design/icons";

const { Text, Title } = Typography;

interface StatCardProps {
    title: string;
    value: string | number;
    trend?: string;
    negative?: boolean;
}

const StatCard = ({ title, value, trend, negative }: StatCardProps) => {
    const { token } = theme.useToken();

    return (
        <Card
            style={{
                borderRadius: token.borderRadiusLG,
                border: `1px solid ${token.colorBorderSecondary}`,
                background: token.colorBgElevated,
                transition: "transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out",
            }}
            styles={{ body: { padding: "20px 24px" } }}
            hoverable
        >
            <Text
                type="secondary"
                style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}
            >
                {title}
            </Text>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginTop: 8 }}>
                <Title level={3} style={{ margin: 0, fontWeight: 800 }}>
                    {value}
                </Title>
                {trend && (
                    <span
                        style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 2,
                            color: negative ? token.colorError : token.colorSuccess,
                            background: negative
                                ? `${token.colorError}1a`
                                : `${token.colorSuccess}1a`,
                            padding: "2px 8px",
                            borderRadius: token.borderRadius,
                            fontSize: 12,
                            fontWeight: 700,
                        }}
                    >
                        {negative ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
                        {trend}
                    </span>
                )}
            </div>
        </Card>
    );
};

export default StatCard;