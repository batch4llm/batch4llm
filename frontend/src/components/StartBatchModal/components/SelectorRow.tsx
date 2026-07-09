import type { ReactNode } from "react";
import styles from "../StartBatchModal.module.css";
import { IconChevronRight } from "../Icons.tsx";

type Props = {
    icon: ReactNode;
    iconStyle?: React.CSSProperties;
    label: string;
    value?: string;
    emptyText: string;
    sub?: string;
    invalid?: boolean;
    onClick: () => void;
};

export function SelectorRow({ icon, iconStyle, label, value, emptyText, sub, invalid, onClick }: Props) {
    return (
        <button
            type="button"
            className={`${styles.selectorRow}${invalid ? ` ${styles.invalid}` : ""}`}
            onClick={onClick}
        >
            <div className={styles.selectorIcon} style={iconStyle}>{icon}</div>
            <div className={styles.selectorBody}>
                <div className={styles.selectorLabel}>{label}</div>
                {value
                    ? <div className={styles.selectorValue}>{value}</div>
                    : <div className={styles.selectorEmpty}>{emptyText}</div>}
                {sub && <div className={styles.selectorSub}>{sub}</div>}
            </div>
            <IconChevronRight />
        </button>
    );
}
