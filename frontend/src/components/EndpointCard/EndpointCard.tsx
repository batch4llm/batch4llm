import type { Endpoint } from "../../types/Endpoint";
import { logoFor } from "../../utils/providerLogo";
import { timeAgo } from "../../utils/timeAgo";
import styles from "./EndpointCard.module.css";

function maskToken(t: string): string | null {
    if (!t) return null;
    if (t.length < 8) return "••••••••";
    return `${t.slice(0, 2)}••••••••${t.slice(-2)}`;
}

const PULSE_CLASSES: Record<string, string> = {
    ok:   styles.pulseOk,
    down: styles.pulseDown,
    idle: styles.pulseIdle,
};

type Props = {
    endpoint: Endpoint;
};

export function EndpointCard({ endpoint }: Props) {
    const status =
        endpoint.is_healthy === true  ? "ok"
      : endpoint.is_healthy === false ? "down"
      :                                 "idle";
    const pulseClass = PULSE_CLASSES[status] ?? styles.pulseIdle;
    const tokenMasked = maskToken(endpoint.token);
    const checkedAt = endpoint.health_checked_at
        ? timeAgo(endpoint.health_checked_at)
        : null;

    return (
        <div className={styles.card}>
            <span
                className={`${styles.pulse} ${pulseClass}`}
                title={
                    status === "ok"   ? `Healthy${checkedAt ? ` · last checked ${checkedAt}` : ""}`
                  : status === "down" ? `Unreachable${endpoint.health_error ? ` · ${endpoint.health_error}` : ""}${checkedAt ? ` · last checked ${checkedAt}` : ""}`
                  :                     "Awaiting first health check"
                }
            >
                <span className={styles.pulseDot} />
            </span>

            <div className={styles.top}>
                <div className={styles.logo}>
                    <img src={logoFor(endpoint.provider)} alt="" />
                </div>
                <div className={styles.heading}>
                    <h3 className={styles.name} title={endpoint.name}>{endpoint.name}</h3>
                    <div className={styles.meta}>
                        <span>{endpoint.provider}</span>
                        <span className={styles.metaSep}>·</span>
                        <span>{endpoint.client}</span>
                    </div>
                </div>
            </div>

            <dl className={styles.metaList}>
                <div className={styles.metaRow}>
                    <dt>URL</dt>
                    <dd className={!endpoint.url ? styles.ddEmpty : ""} title={endpoint.url}>
                        {endpoint.url || "provider default"}
                    </dd>
                </div>
                <div className={styles.metaRow}>
                    <dt>Token</dt>
                    <dd className={tokenMasked ? styles.ddMono : styles.ddEmpty}>
                        {tokenMasked || "—"}
                    </dd>
                </div>
            </dl>
        </div>
    );
}
