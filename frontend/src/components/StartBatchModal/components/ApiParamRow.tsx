import styles from "../StartBatchModal.module.css";
import { IconReset } from "../Icons.tsx";

type Props = {
    paramKey: string;
    label: string;
    tooltip: string;
    kind: "slider" | "number";
    min?: number;
    max?: number;
    step?: number;
    placeholder?: string;
    value: number | undefined;
    active: boolean;
    alwaysActive?: boolean;
    onChange: (value: number) => void;
    onReset?: () => void;
};

function formatValue(v: number): string {
    return Number.isInteger(v) ? String(v) : v.toFixed(2).replace(/\.?0+$/, "");
}

export function ApiParamRow({
    label, tooltip, kind, min, max, step, placeholder, value, active, alwaysActive, onChange, onReset,
}: Props) {
    const isActive = active || !!alwaysActive;

    return (
        <div className={`${styles.mpRow}${isActive ? ` ${styles.active}` : ""}`}>
            <div className={styles.mpLabelWrap}>
                <span className={styles.mpLabel}>{label}</span>
                <button type="button" className={styles.mpInfo} title={tooltip}>?</button>
            </div>
            <div>
                {kind === "slider" ? (
                    <input
                        type="range"
                        className={styles.mpSlider}
                        min={min}
                        max={max}
                        step={step}
                        value={value ?? min}
                        onChange={(e) => onChange(parseFloat(e.target.value))}
                    />
                ) : (
                    <input
                        type="number"
                        className={styles.mpNumber}
                        min={min}
                        max={max}
                        placeholder={placeholder}
                        value={value ?? ""}
                        onChange={(e) => onChange(e.target.value === "" ? NaN : parseFloat(e.target.value))}
                    />
                )}
            </div>
            <span className={styles.mpValue}>
                {kind === "slider" && value !== undefined ? formatValue(value) : ""}
            </span>
            {!alwaysActive && (
                <button
                    type="button"
                    className={styles.mpReset}
                    onClick={onReset}
                    title="Reset to provider default"
                >
                    <IconReset />
                </button>
            )}
        </div>
    );
}
