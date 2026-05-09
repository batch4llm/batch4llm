import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { LoginAPI } from "../api/login.ts"; // your API service

export default function RequireAuth() {
    const [isLoading, setIsLoading] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        LoginAPI.authenticate()
            .then((res) => {
                setIsAuthenticated(res); // true if logged in, false if not
            })
            .catch(() => {
                setIsAuthenticated(false);
            })
            .finally(() => setIsLoading(false));
    }, []);

    if (isLoading) {
        return <div>Loading...</div>; // Optional: spinner
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <Outlet />; // Render nested routes if authenticated
}
