import styles from "../AddPromptModal.module.css";
import { IconBack, IconChevronRight } from "../Icons.tsx";

type Props = {
    onBack: () => void;
    onSelectYaml: () => void;
    onSelectVisual: () => void;
};

export function ComplexTypeSelectView({ onBack, onSelectYaml, onSelectVisual }: Props) {
    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Complex Prompt</h2>
            </div>
            <p className={styles.viewSub}>Which editor do you want to use?</p>

            <div className={styles.modeGrid}>
                <button type="button" className={styles.modeCard} onClick={onSelectVisual}>
                    <div className={styles.modeCardTitle}>
                        Visual Editor
                        <IconChevronRight />
                    </div>
                    <p className={styles.modeCardDesc}>
                        Separate fields for the pre-prompt, each step and the post-prompt.
                    </p>
                </button>
                <button type="button" className={styles.modeCard} onClick={onSelectYaml}>
                    <div className={styles.modeCardTitle}>
                        YAML
                        <IconChevronRight />
                    </div>
                    <p className={styles.modeCardDesc}>
                        Write the multi_prompt_v1 YAML directly.
                    </p>
                </button>
            </div>
        </div>
    );
}
