import type { Prompt } from "../../types/Prompt.ts";
import { Modal } from "../Modal/Modal.tsx";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./PromptModal.module.css";

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

type Props = {
    prompt: Prompt | null;
    onClose: () => void;
    onEditClone?: (prompt: Prompt) => void;
};

function handleExport(prompt: Prompt) {
    const extension = prompt.multi_prompt ? "yaml" : "txt";
    const blob = new Blob([prompt.content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);

    const link = document.createElement("a");
    link.href = url;
    link.download = `${prompt.name}.${extension}`;
    link.click();

    URL.revokeObjectURL(url);
}

export function PromptModal({ prompt, onClose, onEditClone }: Props) {
    if (!prompt) return null;

    const isMulti = prompt.multi_prompt;
    let content = prompt.content || "";
    if (isMulti) {
        try { content = JSON.stringify(JSON.parse(prompt.content), null, 2); } catch { /* not JSON */ }
    }

    return (
        <Modal isOpen onClose={onClose} className={styles.wideModal}>
            <div className={modalStyles.modalHeader}>
                <div className={modalStyles.modalTypeBadge}>{isMulti ? "MULTI" : "TXT"}</div>
                <div className={modalStyles.modalTitleBlock}>
                    <h3 className={modalStyles.modalTitle}>{prompt.name}</h3>
                    <p className={modalStyles.modalSub}>
                        <span>Created {formatDate(prompt.created_at)}</span>
                        {isMulti && prompt.step_count !== null && (
                            <>
                                <span className={modalStyles.modalSep}>·</span>
                                <span>{prompt.step_count} steps</span>
                            </>
                        )}
                    </p>
                </div>
                <button className={modalStyles.modalClose} onClick={onClose} aria-label="Close">
                    <IconClose />
                </button>
            </div>

            <pre className={styles.content}>{content}</pre>

            <div className={styles.actions}>
                <button className={modalStyles.btnSecondary} onClick={onClose}>Close</button>
                <button className={modalStyles.btnSecondary} onClick={() => handleExport(prompt)}>
                    Export
                </button>
                {onEditClone && (
                    <button className={styles.btnPrimary} onClick={() => onEditClone(prompt)}>
                        Edit/Clone
                    </button>
                )}
            </div>
        </Modal>
    );
}
