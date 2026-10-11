import { Suspense, lazy } from "react";
import { Spin } from "antd";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "../layout/MainLayout";

const DashboardPage = lazy(() => import("@/pages/DashboardPage/DashboardPage"));
const EmployeesPage = lazy(() => import("@/pages/EmployeesPage/EmployeesPage"));
const AttendancePage = lazy(() => import("@/pages/AttendancePage/AttendancePage"));
const LoginPage = lazy(() => import("@/pages/LoginPage/LoginPage"));
const EmployeeDetailPage = lazy(() => import("@/pages/EmployeeDetailPage/EmployeeDetailPage"));
const CreateEmployeePage = lazy(() => import("@/pages/CreateEmployeePage/CreateEmployeePage"));
const StructurePage = lazy(() => import("@/pages/StructurePage/StructurePage"));
const CreateDepartmentPage = lazy(() => import("@/pages/CreateDepartmentPage/CreateDepartmentPage"));
const PayrollPage = lazy(() => import("@/pages/PayrollPage/PayrollPage"));

const routeFallback = (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "50vh" }}>
        <Spin size="large" />
    </div>
);

const AppRouter = () => {
    return (
        <BrowserRouter>
            <Suspense fallback={routeFallback}>
                <Routes>
                    <Route path="/login" element={<LoginPage />} />

                    <Route element={<MainLayout />}>
                        <Route path="/" element={<DashboardPage />} />
                        <Route path="/employees" element={<EmployeesPage />} />
                        <Route path="/employees/create" element={<CreateEmployeePage />} />
                        <Route path="/employees/:id" element={<EmployeeDetailPage />} />
                        <Route path="/structure" element={<StructurePage />} />
                        <Route path="/departments/create" element={<CreateDepartmentPage />} />
                        <Route path="/attendance" element={<AttendancePage />} />
                        <Route path="/payroll" element={<PayrollPage />} />
                    </Route>
                </Routes>
            </Suspense>
        </BrowserRouter>
    );
};

export default AppRouter;
