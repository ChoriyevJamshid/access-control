import { useState } from "react";
import { Layout } from "antd";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { Outlet } from "react-router-dom";
import { useThemeMode } from "@/app/providers/themeContext";

const { Content } = Layout;

const MainLayout = () => {
    const [collapsed, setCollapsed] = useState(false);
    const { mode } = useThemeMode();

    return (
        <Layout style={{ minHeight: "100vh" }}>
            <Sidebar collapsed={collapsed} onCollapse={setCollapsed} />
            <Layout style={{ background: mode === "dark" ? "#0a0a0a" : "#f1f5f9" }}>
                <Topbar />
                <Content
                    style={{
                        padding: "24px",
                        overflow: "auto",
                        minHeight: "calc(100vh - 56px)",
                    }}
                >
                    <Outlet />
                </Content>
            </Layout>
        </Layout>
    );
};

export default MainLayout;
