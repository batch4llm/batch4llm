import type { Prompt } from "../../types/Prompt";
import styles from "./PromptCard.module.css";

function formatDate(s: string): string {
    if (!s) return "—";
    const d = new Date(s);
    if (Number.isNaN(d.getTime())) return s;
    return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function IconTrash() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 6h18"/>
            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
        </svg>
    );
}

type Props = {
    prompt: Prompt;
    onDelete?: (prompt: Prompt) => void;
};

export function PromptCard({ prompt, onDelete }: Props) {
    const isMulti = prompt.multi_prompt;
    const stepCount = prompt.step_count;

    let preview = prompt.content || "";
    if (isMulti) {
        try { preview = JSON.stringify(JSON.parse(prompt.content), null, 2); } catch { /* not JSON */ }
    }

    return (
        <div className={`${styles.card} ${isMulti ? styles.cardMulti : ""}`}>
            <div className={styles.head}>
                <h3 className={styles.name} title={prompt.name}>{prompt.name}</h3>
                {isMulti && (
                    <span className={styles.tag} title="Multi-prompt — split into separate model requests">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                             strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                            <line x1="8" y1="6" x2="21" y2="6"/>
                            <line x1="8" y1="12" x2="21" y2="12"/>
                            <line x1="8" y1="18" x2="21" y2="18"/>
                            <line x1="3" y1="6" x2="3.01" y2="6"/>
                            <line x1="3" y1="12" x2="3.01" y2="12"/>
                            <line x1="3" y1="18" x2="3.01" y2="18"/>
                        </svg>
                        multi
                        {stepCount !== null && (
                            <span className={styles.tagCount}>· {stepCount} steps</span>
                        )}
                    </span>
                )}
            </div>

            <pre className={`${styles.preview} ${isMulti ? styles.previewCode : ""}`}>
                {preview}
            </pre>

            <div className={styles.foot}>
                <span>{formatDate(prompt.created_at)}</span>
                {onDelete && (
                    <button
                        className={styles.deleteBtn}
                        title="Delete prompt"
                        onClick={() => onDelete(prompt)}
                    >
                        <IconTrash />
                    </button>
                )}
            </div>
        </div>
    );
}
