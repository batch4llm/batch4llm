import styles from "../AddPromptModal.module.css";
import { IconChevronRight } from "../Icons.tsx";

type Props = {
    onSelectSimple: () => void;
    onSelectComplex: () => void;
};

export function TypeSelectView({ onSelectSimple, onSelectComplex }: Props) {
    return (
        <div className={styles.view}>
            <h2 className={styles.viewTitle}>Add Prompt</h2>
            <p className={styles.viewSub}>How do you want to build this prompt?</p>

            <div className={styles.modeGrid}>
                <button type="button" className={styles.modeCard} onClick={onSelectSimple}>
                    <div className={styles.modeCardTitle}>
                        Simple
                        <IconChevronRight />
                    </div>
                    <p className={styles.modeCardDesc}>
                        A single block of text sent to the model as-is.
                    </p>
                </button>
                <button type="button" className={styles.modeCard} onClick={onSelectComplex}>
                    <div className={styles.modeCardTitle}>
                        Complex
                        <IconChevronRight />
                    </div>
                    <p className={styles.modeCardDesc}>
                        Multiple steps, optionally wrapped in a shared pre/post prompt.
                    </p>
                </button>
            </div>
        </div>
    );
}
