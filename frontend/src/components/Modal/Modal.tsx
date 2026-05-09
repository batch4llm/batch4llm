import styles from "./Modal.module.css";

type ModalProps = {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
    className?: string;
};

export function Modal({ isOpen, onClose, children, className }: ModalProps) {
    if (!isOpen) return null;

    return (
        <div className={styles.backdrop} onMouseDown={onClose}>
            <div
                className={[styles.modal, className].filter(Boolean).join(" ")}
                onMouseDown={(e) => e.stopPropagation()}
            >
                {children}
            </div>
        </div>
    );
}
