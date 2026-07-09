import type { Prompt } from "../../../types/Prompt";
import styles from "../StartBatchModal.module.css";
import { IconBack, IconCheck } from "../Icons.tsx";

type Props = {
    prompts: Prompt[];
    loading: boolean;
    selectedPrompt: Prompt | null;
    onSelect: (prompt: Prompt) => void;
    onBack: () => void;
};

export function PromptView({ prompts, loading, selectedPrompt, onSelect, onBack }: Props) {
    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Select Prompt</h2>
            </div>

            <div className={styles.cardList}>
                {loading && <div className={styles.emptyNote}>Loading...</div>}
                {!loading && prompts.length === 0 && <div className={styles.emptyNote}>No prompts available.</div>}
                {prompts.map((p) => {
                    const selected = selectedPrompt?.id === p.id;
                    return (
                        <button
                            type="button"
                            key={p.id}
                            className={`${styles.card}${selected ? ` ${styles.selected}` : ""}`}
                            onClick={() => onSelect(p)}
                        >
                            <div className={styles.cardTop}>
                                <div className={styles.cardName}>{p.name}</div>
                                <span className={`${styles.cardBadge}${p.multi_prompt ? ` ${styles.multi}` : ""}`}>
                                    {p.multi_prompt ? "Multi-step" : "1 step"}
                                </span>
                            </div>
                            <div className={styles.cardPreview}>{p.content}</div>
                            <div className={styles.cardSelectedBadge}>
                                <IconCheck size={12} /> Selected
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
