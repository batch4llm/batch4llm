import styles from "../StartBatchModal.module.css";
import { IconBack } from "../Icons.tsx";

type Props = {
    text: string;
    onTextChange: (text: string) => void;
    onClear: () => void;
    onConfirm: () => void;
    onBack: () => void;
};

export function SampleOutputView({ text, onTextChange, onClear, onConfirm, onBack }: Props) {
    const tokens = Math.round(text.length / 4);

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Sample Output</h2>
            </div>

            <p className={styles.sampleIntro}>
                Paste a typical model response for <strong>one task</strong>. The estimator uses this to calculate output tokens — no manual counting needed.
            </p>

            <textarea
                className={styles.sampleTextarea}
                placeholder="Paste a sample model output here..."
                value={text}
                onChange={(e) => onTextChange(e.target.value)}
            />

            <div className={styles.sampleStatsRow}>
                <div className={styles.sampleStats}>
                    ~<span className={styles.sampleStatsCount}>{tokens.toLocaleString()}</span> tokens
                    &nbsp;·&nbsp;
                    <span>{text.length.toLocaleString()} chars</span>
                </div>
                <div className={styles.sampleActions}>
                    <button type="button" className={styles.btnGhostSm} onClick={onClear}>Clear</button>
                    <button type="button" className={styles.btnPrimarySm} onClick={onConfirm}>Use this sample</button>
                </div>
            </div>
        </div>
    );
}
