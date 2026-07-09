import type { ReactNode } from "react";
import styles from "../StartBatchModal.module.css";

type Props = {
    title: string;
    open: boolean;
    onToggle: () => void;
    children: ReactNode;
    style?: React.CSSProperties;
};

export function Collapsible({ title, open, onToggle, children, style }: Props) {
    return (
        <div className={styles.collapsible} style={style}>
            <button type="button" className={styles.collapsibleHeader} onClick={onToggle}>
                <span className={`${styles.collapsibleArrow}${open ? ` ${styles.open}` : ""}`}>▶</span>
                {title}
            </button>
            {open && <div className={styles.collapsibleBody}>{children}</div>}
        </div>
    );
}
