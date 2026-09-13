import styles from "../AddPromptModal.module.css";
import { IconBack } from "../Icons.tsx";

type Props = {
    title?: string;
    name: string;
    onSetName: (v: string) => void;
    content: string;
    onSetContent: (v: string) => void;
    onBack: () => void;
    onSubmit: () => void;
};

export function SimpleView({ title, name, onSetName, content, onSetContent, onBack, onSubmit }: Props) {
    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>{title ?? "Simple Prompt"}</h2>
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
                    placeholder="Write your prompt here..."
                    required
                    minLength={3}
                    rows={10}
                    value={content}
                    onChange={(e) => onSetContent(e.target.value)}
                />

                <button type="submit">Add</button>
            </form>
        </div>
    );
}
