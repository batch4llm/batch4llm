import styles from "./Modal.module.css";

type ModalProps = {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
    className?: string;
    style?: React.CSSProperties;
};

export function Modal({ isOpen, onClose, children, className, style }: ModalProps) {
    if (!isOpen) return null;

    return (
        <div className={styles.backdrop} onMouseDown={onClose}>
            <div
                className={[styles.modal, className].filter(Boolean).join(" ")}
                style={style}
                onMouseDown={(e) => e.stopPropagation()}
            >
                {children}
            </div>
        </div>
    );
}
