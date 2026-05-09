import { Link, useLocation } from "react-router-dom";
import styles from "./NotFoundPage.module.css";

export default function NotFoundPage() {
    const { pathname } = useLocation();

    return (
        <section className={styles.section}>
            <h2 className={styles.code}>404</h2>
            <p className={styles.message}>Page not found</p>
            <p className={styles.path}>{pathname}</p>
            <Link className={styles.link} to="/">Back to home</Link>
        </section>
    );
}
