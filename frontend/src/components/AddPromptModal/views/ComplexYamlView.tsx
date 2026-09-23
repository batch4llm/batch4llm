import styles from "../AddPromptModal.module.css";
import { IconBack } from "../Icons.tsx";
import { validateMultiPromptContent } from "../../../utils/multiPromptYaml.ts";

type Props = {
    title?: string;
    name: string;
    onSetName: (v: string) => void;
    content: string;
    onSetContent: (v: string) => void;
    canSwitchToVisual: boolean;
    onSwitchToVisual: () => void;
    onBack: () => void;
    onSubmit: () => void;
};

export function ComplexYamlView({
    title, name, onSetName, content, onSetContent, canSwitchToVisual, onSwitchToVisual, onBack, onSubmit,
}: Props) {
    const error = validateMultiPromptContent(content);

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>{title ?? "Complex Prompt · YAML"}</h2>
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

                <textarea
                    placeholder="multi_prompt_v1:\n  tasks:\n    - id: step_1\n      prompt: ..."
                    className={styles.yamlTextarea}
                    required
                    minLength={3}
                    rows={14}
                    value={content}
                    onChange={(e) => onSetContent(e.target.value)}
                />

                {error && <div className={styles.errorBox}>{error}</div>}

                <div className={styles.switchRow}>
                    <button
                        type="button"
                        className={styles.btnGhostSm}
                        disabled={!canSwitchToVisual}
                        title={canSwitchToVisual ? undefined : "This YAML doesn't match the visual editor's format (invalid YAML, unknown fields, or no tasks)"}
                        onClick={onSwitchToVisual}
                    >
                        Switch to Visual Editor
                    </button>
                    <button type="submit">Add</button>
                </div>
            </form>
        </div>
    );
}
