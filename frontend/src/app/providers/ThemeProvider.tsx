import { useState, useMemo } from "react";
import type { ReactNode } from "react";
import { ConfigProvider, theme as antTheme } from "antd";
import ruRU from "antd/locale/ru_RU";
import { ThemeContext } from "./themeContext";

export default function ThemeProvider({ children }: { children: ReactNode }) {
    const [mode, setMode] = useState<"light" | "dark">("dark");

    const toggleMode = () => setMode((prev) => (prev === "dark" ? "light" : "dark"));

    const algorithm = useMemo(
        () => (mode === "dark" ? antTheme.darkAlgorithm : antTheme.defaultAlgorithm),
        [mode]
    );

    return (
        <ThemeContext.Provider value={{ mode, toggleMode }}>
            <ConfigProvider
                locale={ruRU}
                theme={{
                    algorithm,
                    token: {
                        colorPrimary: "#3b82f6",
                        colorLink: "#3b82f6",
                        borderRadius: 10,
                        fontFamily: "'Inter', sans-serif",
                    },
                    components: {
                        Layout: {
                            siderBg: mode === "dark" ? "#141414" : "#ffffff",
                            headerBg: mode === "dark" ? "#141414" : "#ffffff",
                            bodyBg: mode === "dark" ? "#000000" : "#f1f5f9",
                        },
                        Menu: {
                            darkItemBg: "#141414",
                            darkSubMenuItemBg: "#141414",
                        },
                        Table: {
                            headerBg: mode === "dark" ? "#1d1d1d" : "#f8fafc",
                            rowHoverBg: mode === "dark" ? "rgba(255,255,255,0.08)" : "#f0f7ff",
                        },
                    },
                }}
            >
                {children}
            </ConfigProvider>
        </ThemeContext.Provider>
    );
}
