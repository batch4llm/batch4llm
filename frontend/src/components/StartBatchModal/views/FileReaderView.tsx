import styles from "../StartBatchModal.module.css";
import { IconBack, IconCheck } from "../Icons.tsx";

type Props = {
    fileReaders: string[];
    loading: boolean;
    selectedFileReader: string | null;
    onSelect: (readerId: string) => void;
    onBack: () => void;
};

function prettifyReaderId(id: string): string {
    return id.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

export function FileReaderView({ fileReaders, loading, selectedFileReader, onSelect, onBack }: Props) {
    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Select File Reader</h2>
            </div>

            <div className={styles.cardList}>
                {loading && <div className={styles.emptyNote}>Loading...</div>}
                {!loading && fileReaders.length === 0 && <div className={styles.emptyNote}>No file readers available.</div>}
                {fileReaders.map((id) => {
                    const selected = selectedFileReader === id;
                    return (
                        <button
                            type="button"
                            key={id}
                            className={`${styles.card}${selected ? ` ${styles.selected}` : ""}`}
                            onClick={() => onSelect(id)}
                        >
                            <div className={styles.cardTop}>
                                <div className={styles.cardName}>{prettifyReaderId(id)}</div>
                            </div>
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
