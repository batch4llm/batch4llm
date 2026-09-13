import type { PromptTask } from "../../../utils/multiPromptYaml.ts";
import styles from "../AddPromptModal.module.css";
import { IconBack } from "../Icons.tsx";
import { StepRow } from "../components/StepRow.tsx";

type Props = {
    title?: string;
    name: string;
    onSetName: (v: string) => void;
    pre: string;
    onSetPre: (v: string) => void;
    post: string;
    onSetPost: (v: string) => void;
    tasks: PromptTask[];
    onSetTasks: (tasks: PromptTask[]) => void;
    onSwitchToYaml: () => void;
    onBack: () => void;
    onSubmit: () => void;
};

export function ComplexVisualView({
    title, name, onSetName, pre, onSetPre, post, onSetPost, tasks, onSetTasks, onSwitchToYaml, onBack, onSubmit,
}: Props) {
    function updateTask(index: number, task: PromptTask) {
        onSetTasks(tasks.map((t, i) => (i === index ? task : t)));
    }

    function removeTask(index: number) {
        onSetTasks(tasks.filter((_, i) => i !== index));
    }

    function addTask() {
        const existingIds = new Set(tasks.map(t => t.id));
        let n = tasks.length + 1;
        while (existingIds.has(`step_${n}`)) n++;
        onSetTasks([...tasks, { id: `step_${n}`, prompt: "" }]);
    }

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>{title ?? "Complex Prompt · Visual Editor"}</h2>
            </div>

            <form
                className={styles.promptForm}
                onSubmit={(e) => { e.preventDefault(); onSubmit(); }}
            >
                <input
                    type="text"
                    placeholder="Name"
                    required
                    minLength={3}
                    value={name}
                    onChange={(e) => onSetName(e.target.value)}
                />

                <div className={styles.visualField}>
                    <label className={styles.visualFieldLabel}>Pre-Prompt <span>optional, prepended to every step</span></label>
                    <textarea
                        placeholder="Shared instructions before each step..."
                        rows={3}
                        value={pre}
                        onChange={(e) => onSetPre(e.target.value)}
                    />
                </div>

                <div className={styles.stepList}>
                    {tasks.map((task, i) => (
                        <StepRow
                            key={i}
                            index={i}
                            task={task}
                            onChange={(t) => updateTask(i, t)}
                            onRemove={() => removeTask(i)}
                            removable={tasks.length > 1}
                        />
                    ))}
                </div>
                <button type="button" className={styles.addStepBtn} onClick={addTask}>
                    + Add Step
                </button>

                <div className={styles.visualField}>
                    <label className={styles.visualFieldLabel}>Post-Prompt <span>optional, appended to every step</span></label>
                    <textarea
                        placeholder="Shared instructions after each step..."
                        rows={3}
                        value={post}
                        onChange={(e) => onSetPost(e.target.value)}
                    />
                </div>

                <div className={styles.switchRow}>
                    <button type="button" className={styles.btnGhostSm} onClick={onSwitchToYaml}>
                        Switch to YAML
                    </button>
                    <button type="submit">Add</button>
                </div>
            </form>
        </div>
    );
}
