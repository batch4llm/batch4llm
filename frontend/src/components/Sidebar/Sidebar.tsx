import { useEffect, useState } from "react";
import {NavLink, useNavigate} from "react-router-dom";
import styles from "./Sidebar.module.css";
import { UserAPI } from "../../api/user.ts";

export default function Sidebar() {

    const navigate = useNavigate();
    const [username, setUsername] = useState<string | null>(null);

    useEffect(() => {
        UserAPI.getMe().then(u => setUsername(u.username)).catch(() => {});
    }, []);

    const initial = username?.[0]?.toUpperCase() ?? "?";

    return (
        <aside className={styles.sidebar}>
            <div className={styles.sidebarTop}>
                <h2>Batch4LLM</h2>
                <nav>
                    <NavLink to="/" end className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Batch Run
                    </NavLink>
                    <NavLink to="/export" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Export
                    </NavLink>
                    <NavLink to="/files" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Files
                    </NavLink>
                    <NavLink to="/prompts" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Prompts
                    </NavLink>
                    <NavLink to="/endpoints" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Endpoints
                    </NavLink>
                </nav>
            </div>

            <div className={styles.sidebarFooter}>
                <button className={styles.profileButton} onClick={() => navigate("/account")}>
                    <span className={styles.sidebarAvatar}>{initial}</span>
                    <span>{username ?? "…"}</span>
                </button>
            </div>
        </aside>
    );
}
