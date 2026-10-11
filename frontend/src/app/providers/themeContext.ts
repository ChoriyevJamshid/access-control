import { createContext, useContext } from "react";

export interface ThemeContextType {
    mode: "light" | "dark";
    toggleMode: () => void;
}

export const ThemeContext = createContext<ThemeContextType>({
    mode: "dark",
    toggleMode: () => {},
});

export const useThemeMode = () => useContext(ThemeContext);
