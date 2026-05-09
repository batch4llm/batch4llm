import {NavLink, useNavigate} from "react-router-dom";
import styles from "./Sidebar.module.css";
import { LoginAPI } from "../../api/login.ts"

export default function Sidebar() {

    const navigate = useNavigate();

    function handleLogout() {
        LoginAPI.logout().then((res) => {
            if(res) {
                navigate("/login")
            }
        }).catch((err) => {
            console.log(err);
            alert(err)
        })
    }

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
                <button className={styles.logoutButton} onClick={handleLogout}>Logout</button>
            </div>
        </aside>
    );
}
