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
                    <NavLink to="/files" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Files
                    </NavLink>
                    <NavLink to="/prompts" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Prompts
                    </NavLink>
                    <NavLink to="/endpoints" className={({ isActive }) => isActive ? styles.activeLink : undefined}>
                        Endpoints
                    </NavLink>
                    <a href="https://docs.batch4llm.de" target="_blank" rel="noopener noreferrer" className={styles.externalLink}>
                        Docs
                        <svg viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" width="11" height="11" aria-hidden="true">
                            <path d="M5 2H2a1 1 0 0 0-1 1v7a1 1 0 0 0 1 1h7a1 1 0 0 0 1-1V7" />
                            <path d="M8 1h3v3" />
                            <path d="M11 1 5.5 6.5" />
                        </svg>
                    </a>
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
