import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { UserAPI } from "../../api/user";
import type { User, Group } from "../../api/user";
import { LoginAPI } from "../../api/login";
import styles from "./AccountPage.module.css";

export default function AccountPage() {
    const navigate = useNavigate();
    const [user, setUser] = useState<User | null>(null);
    const [group, setGroup] = useState<Group | null | "loading">("loading");

    const [oldPassword, setOldPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [pwFeedback, setPwFeedback] = useState<{ ok: boolean; msg: string } | null>(null);

    useEffect(() => {
        UserAPI.getMe().then(setUser);
        UserAPI.getGroup().then(setGroup);
    }, []);

    function handleLogout() {
        LoginAPI.logout().then(ok => {
            if (ok) navigate("/login");
        }).catch(err => {
            console.error(err);
            alert(err);
        });
    }

    function handleChangePassword(e: React.FormEvent) {
        e.preventDefault();
        setPwFeedback(null);

        if (newPassword !== confirmPassword) {
            setPwFeedback({ ok: false, msg: "New passwords do not match." });
            return;
        }

        LoginAPI.changePassword(oldPassword, newPassword)
            .then(ok => {
                if (ok) {
                    setPwFeedback({ ok: true, msg: "Password changed successfully." });
                    setOldPassword("");
                    setNewPassword("");
                    setConfirmPassword("");
                } else {
                    setPwFeedback({ ok: false, msg: "Failed to change password." });
                }
            })
            .catch(() => {
                setPwFeedback({ ok: false, msg: "Incorrect current password." });
            });
    }

    const initials = user?.username?.[0]?.toUpperCase() ?? "?";

    return (
        <div className={styles.page}>
            {/* Section 1 – User Profile */}
            <div className="card">
                <div className={styles.profileRow}>
                    <div className={styles.avatar}>{initials}</div>
                    <div>
                        <h2 className={styles.username}>{user?.username ?? "…"}</h2>
                        <p className={styles.muted}>ID: {user?.id ?? "…"}</p>
                        <div className={styles.badges}>
                            {user?.is_admin && <span className={styles.badge}>Admin</span>}
                            {user?.is_supervisor && <span className={styles.badge}>Supervisor</span>}
                        </div>
                    </div>
                </div>
            </div>

            {/* Section 2 – Group */}
            <div className="card">
                <h3 className={styles.sectionHeading}>Group</h3>
                {group === "loading" && <p className={styles.muted}>Loading…</p>}
                {group === null && <p className={styles.muted}>You are not assigned to a group.</p>}
                {group && group !== "loading" && (
                    <>
                        <p className={styles.groupName}>{group.name}</p>
                        <ul className={styles.memberList}>
                            {group.users.map(u => (
                                <li key={u.id}>{u.username}</li>
                            ))}
                        </ul>
                    </>
                )}
            </div>

            {/* Section 3 – Change Password */}
            <div className="card">
                <h3 className={styles.sectionHeading}>Change Password</h3>
                <form onSubmit={handleChangePassword} className={styles.pwForm}>
                    <label className={styles.label}>
                        Current password
                        <input
                            type="password"
                            value={oldPassword}
                            onChange={e => setOldPassword(e.target.value)}
                            required
                        />
                    </label>
                    <label className={styles.label}>
                        New password
                        <input
                            type="password"
                            value={newPassword}
                            onChange={e => setNewPassword(e.target.value)}
                            required
                        />
                    </label>
                    <label className={styles.label}>
                        Confirm new password
                        <input
                            type="password"
                            value={confirmPassword}
                            onChange={e => setConfirmPassword(e.target.value)}
                            required
                        />
                    </label>
                    {pwFeedback && (
                        <p className={pwFeedback.ok ? styles.success : styles.error}>
                            {pwFeedback.msg}
                        </p>
                    )}
                    <button type="submit">Change Password</button>
                </form>
            </div>

            {/* Section 4 – Logout */}
            <div className="card">
                <button className={styles.logoutButton} onClick={handleLogout}>Logout</button>
            </div>
        </div>
    );
}
