import type { PromptTask } from "../../../utils/multiPromptYaml.ts";
import styles from "../AddPromptModal.module.css";

type Props = {
    index: number;
    task: PromptTask;
    onChange: (task: PromptTask) => void;
    onRemove: () => void;
    removable: boolean;
};

export function StepRow({ index, task, onChange, onRemove, removable }: Props) {
    return (
        <div className={styles.stepRow}>
            <div className={styles.stepRowHeader}>
                <span className={styles.stepRowIndex}>Step {index + 1}</span>
                <input
                    type="text"
                    className={styles.stepIdInput}
                    placeholder="id"
                    required
                    value={task.id}
                    onChange={(e) => onChange({ ...task, id: e.target.value })}
                />
                <button
                    type="button"
                    className={styles.stepRemoveBtn}
                    disabled={!removable}
                    title={removable ? "Remove step" : "At least one step is required"}
                    onClick={onRemove}
                >
                    ×
                </button>
            </div>
            <textarea
                placeholder="Write this step's prompt here..."
                required
                rows={4}
                value={task.prompt}
                onChange={(e) => onChange({ ...task, prompt: e.target.value })}
            />
        </div>
    );
}
