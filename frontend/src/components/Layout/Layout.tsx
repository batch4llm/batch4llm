import { Outlet } from "react-router-dom";
import Sidebar from "../Sidebar/Sidebar.tsx";
import styles from "./Layout.module.css";

export default function Layout() {
    return (
        <div className={styles.layout}>
            <div className={styles.sidebar}>
                <Sidebar />
            </div>
            <div className={styles.main}>
                <Outlet />
            </div>
        </div>
    );
}
