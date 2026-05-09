import {useState, useEffect} from "react";
import {useNavigate, Link} from "react-router-dom";
import { LoginAPI } from "../../api/login.ts";
import styles from "../RegisterPage/RegisterPage.module.css";

export default function RegisterPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirm_password, setConfirmPassword] = useState("");
    const [firstUser, setFirstUser] = useState(false);
    const [passwordError, setPasswordError] = useState("");
    const [passwordTouched, setPasswordTouched] = useState(false);
    const [confirmPasswordTouched, setConfirmPasswordTouched] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        LoginAPI.first_user().then(setFirstUser);
    }, []);

    function validatePassword() {
        if (password.length < 6) {
            setPasswordError("The password needs to be at least 6 characters long.");
            return false;
        }
        else if(confirmPasswordTouched && (password !== confirm_password)) {
            setPasswordError("The passwords do not match.");
        }
        else {
            setPasswordError("");
            return true;
        }
    }

    const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setPassword(e.target.value);
        if (passwordTouched) validatePassword();
    };

    const handleConfirmPasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setConfirmPassword(e.target.value);
        if (confirmPasswordTouched) validatePassword();
    };

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!validatePassword()) return;

        LoginAPI.register(username, password)
            .then((result) => {
                if (result) navigate("/login");
            })
            .catch((error) => {
                console.log(error);
                alert(error);
            });
    }

    return (
        <section className={styles.section}>
            <h2 className={styles.h2}>Batch4LLM</h2>
            <form className={styles.form} onSubmit={handleSubmit}>
                {firstUser && <p className={styles.p}>You are creating the admin account!</p>}
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
                    onChange={handlePasswordChange}
                    onBlur={() => {
                        setPasswordTouched(true);
                        validatePassword();
                    }}
                />
                <input
                    className={styles.input}
                    type="password"
                    placeholder="Confirm Password"
                    value={confirm_password}
                    minLength={6}
                    onChange={handleConfirmPasswordChange}
                    onBlur={() => {
                        setConfirmPasswordTouched(true);
                        validatePassword();
                    }}
                />
                {passwordTouched && passwordError && (
                    <p className={styles.error}>{passwordError}</p>
                )}
                <button className={styles.button} type="submit">Register</button>
                <p>Already have an account? <Link to="/login">Login here</Link></p>
            </form>
        </section>
    );
}
