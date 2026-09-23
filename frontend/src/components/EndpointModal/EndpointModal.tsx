import { useState } from "react";
import type { Endpoint } from "../../types/Endpoint.ts";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { logoFor } from "../../utils/providerLogo.ts";
import { timeAgo } from "../../utils/timeAgo.ts";
import { Modal } from "../Modal/Modal.tsx";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./EndpointModal.module.css";

function IconClose() {
    return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
    );
}

function formatDate(s: string): string {
    if (!s) return "—";
    const d = new Date(s);
    if (Number.isNaN(d.getTime())) return s;
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function maskToken(t: string | null | undefined): string | null {
    if (!t) return null;
    if (t.length < 8) return "••••••••";
    return `${t.slice(0, 2)}••••••••${t.slice(-2)}`;
}

type Props = {
    endpoint: Endpoint | null;
    onClose: () => void;
    onUpdated: (endpoint: Endpoint) => void;
};

export function EndpointModal({ endpoint, onClose, onUpdated }: Props) {
    const [url, setUrl] = useState(endpoint?.url ?? "");
    const [token, setToken] = useState("");
    const [wasOpen, setWasOpen] = useState(!!endpoint);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<{ success: boolean; error?: string } | null>(null);

    // Re-fill the form whenever the modal is (re-)opened for a (possibly
    // different) endpoint, without resetting fields the user is editing
    // while it's already open.
    const isOpen = !!endpoint;
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) {
            setUrl(endpoint?.url ?? "");
            setToken("");
            setTestResult(null);
        }
    }

    if (!endpoint) return null;

    const status =
        endpoint.is_healthy === true  ? "ok"
      : endpoint.is_healthy === false ? "down"
      :                                 "idle";
    const tokenMasked = maskToken(endpoint.token);
    const dirty = url.trim() !== (endpoint.url ?? "") || token.trim() !== "";

    function handleTest() {
        setTesting(true);
        setTestResult(null);
        EndpointsAPI.test({
            name: endpoint!.name,
            client: endpoint!.client,
            provider: endpoint!.provider,
            url: url.trim() || undefined,
            token: token.trim() || undefined,
        }).then((data) => {
            setTestResult(data.success ? { success: true } : { success: false, error: data.error });
        }).catch((err: unknown) => {
            setTestResult({ success: false, error: String(err) });
        }).finally(() => setTesting(false));
    }

    function handleSave() {
        const payload: { url?: string | null; token?: string } = {};
        if (url.trim() !== (endpoint!.url ?? "")) payload.url = url.trim() === "" ? null : url.trim();
        if (token.trim() !== "") payload.token = token.trim();
        if (Object.keys(payload).length === 0) return;

        setSaving(true);
        setTestResult(null);
        EndpointsAPI.update(endpoint!.id, payload)
            .then((updated) => {
                onUpdated(updated);
                setUrl(updated.url ?? "");
                setToken("");
            })
            .catch((err) => alert(err?.response?.data?.detail || "Endpoint could not be updated."))
            .finally(() => setSaving(false));
    }

    return (
        <Modal isOpen onClose={onClose} className={styles.wideModal}>
            <div className={modalStyles.modalHeader}>
                <div className={`${modalStyles.modalTypeBadge} ${styles.logoBadge}`}>
                    <img src={logoFor(endpoint.provider)} alt="" />
                </div>
                <div className={modalStyles.modalTitleBlock}>
                    <h3 className={modalStyles.modalTitle}>{endpoint.name}</h3>
                    <p className={modalStyles.modalSub}>
                        <span className={`${styles.statusDot} ${styles[`status_${status}`]}`} />
                        <span>{endpoint.provider}</span>
                        <span className={modalStyles.modalSep}>·</span>
                        <span>{endpoint.client}</span>
                        <span className={modalStyles.modalSep}>·</span>
                        <span>Created {formatDate(endpoint.created_at)}</span>
                    </p>
                </div>
                <button className={modalStyles.modalClose} onClick={onClose} aria-label="Close">
                    <IconClose />
                </button>
            </div>

            {testResult ? (
                testResult.success ? (
                    <div className={styles.successBox}>Connection succeeded.</div>
                ) : (
                    <div className={styles.errorBox}>
                        <div className={styles.errorBoxTitle}>Connection failed</div>
                        <div className={styles.errorBoxMessage}>{testResult.error || "Unknown error."}</div>
                    </div>
                )
            ) : status === "down" ? (
                <div className={styles.errorBox}>
                    <div className={styles.errorBoxTitle}>
                        Health check failed
                        {endpoint.health_checked_at && ` · ${timeAgo(endpoint.health_checked_at)}`}
                    </div>
                    <div className={styles.errorBoxMessage}>{endpoint.health_error || "Endpoint unreachable."}</div>
                </div>
            ) : status === "ok" ? (
                <p className={styles.healthNote}>
                    Healthy{endpoint.health_checked_at && ` · last checked ${timeAgo(endpoint.health_checked_at)}`}
                </p>
            ) : null}

            <div className={styles.field}>
                <label className={styles.label}>URL</label>
                <input
                    className={styles.input}
                    type="url"
                    placeholder="provider default"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                />
            </div>

            <div className={styles.field}>
                <label className={styles.label}>API Key</label>
                <input
                    className={styles.input}
                    type="password"
                    placeholder={tokenMasked ? `Current key: ${tokenMasked} — leave blank to keep` : "No key set"}
                    value={token}
                    onChange={(e) => setToken(e.target.value)}
                />
            </div>

            <div className={styles.footer}>
                <button className={modalStyles.btnSecondary} onClick={onClose}>Close</button>
                <div className={styles.footerRight}>
                    <button className={modalStyles.btnSecondary} onClick={handleTest} disabled={testing}>
                        {testing ? "Testing…" : "Test Connection"}
                    </button>
                    <button className={styles.btnPrimary} onClick={handleSave} disabled={!dirty || saving}>
                        {saving ? "Saving…" : "Save changes"}
                    </button>
                </div>
            </div>
        </Modal>
    );
}
