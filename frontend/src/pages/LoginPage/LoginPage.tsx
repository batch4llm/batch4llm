import {useState} from "react";
import {useNavigate} from "react-router-dom";
import { LoginAPI } from "../../api/login.ts";
import styles from "../LoginPage/LoginPage.module.css"

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        LoginAPI.login(username, password).then((result) => {
            if (result) {
                navigate("/")
            }
        }).catch((error) => {
            console.log(error);
            alert(error);
        })
    }

    return (
        <section className={styles.section}>
            <h2 className={styles.h2}>Batch4LLM</h2>
            <form className={styles.form} onSubmit={handleSubmit}>
                <input
                    className={styles.input}
                    type="text"
                    placeholder="Username"
                    value={username}
                    minLength={3}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    className={styles.input}
                    type="password"
                    placeholder="Password"
                    value={password}
                    minLength={6}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <button className={styles.button} type="submit">Login</button>
            </form>
        </section>

    );
}
