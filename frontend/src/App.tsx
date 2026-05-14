import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout/Layout";
import BatchesPage from "./pages/BatchesPage/BatchesPage";
import PromptsPage from "./pages/PromptsPage/PromptsPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import RequireAuth from "./components/RequireAuth";
import FilesPage from "./pages/FilesPage/FilesPage.tsx";
import EndpointsPage from "./pages/EndpointsPage/EndpointsPage.tsx";
import ExportPage from "./pages/ExportPage/ExportPage.tsx";
import NotFoundPage from "./pages/NotFoundPage/NotFoundPage.tsx";
import AccountPage from "./pages/AccountPage/AccountPage.tsx";


export default function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<LoginPage />} />

                <Route element={<RequireAuth />}>
                    <Route element={<Layout />}>
                        <Route path="/" element={<BatchesPage />} />
                        <Route path="/prompts" element={<PromptsPage />} />
                        <Route path="/files" element={<FilesPage />} />
                        <Route path="/endpoints" element={<EndpointsPage />} />
                        <Route path="/export" element={<ExportPage />} />
                        <Route path="/account" element={<AccountPage />} />
                    </Route>
                </Route>

                <Route path="*" element={<NotFoundPage />} />
            </Routes>
        </BrowserRouter>
    );
}
