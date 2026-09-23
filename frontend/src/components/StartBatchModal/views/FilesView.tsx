import type { FileData } from "../../../types/FileData";
import { FileTag } from "../../FileTag/FileTag.tsx";
import styles from "../StartBatchModal.module.css";
import { IconBack } from "../Icons.tsx";

type Props = {
    files: FileData[];
    loading: boolean;
    fileTags: string[];
    selectedFileTags: string[];
    onToggleTag: (tag: string) => void;
    onDone: () => void;
};

function formatSize(bytes?: number): string {
    if (!bytes) return "—";
    if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    if (bytes >= 1024) return (bytes / 1024).toFixed(0) + " KB";
    return bytes + " B";
}

export function FilesView({
    files, loading, fileTags, selectedFileTags, onToggleTag, onDone,
}: Props) {
    const matchedFiles = files.filter(f => selectedFileTags.some(t => f.tags?.includes(t)));
    const noTagsSelected = selectedFileTags.length === 0;

    return (
        <div className={`${styles.view} ${styles.viewFlex}`}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onDone}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Select Files</h2>
                {matchedFiles.length > 0 && <span className={styles.badgeCount}>{matchedFiles.length} selected</span>}
            </div>

            <div className={styles.filesHeroHeadline}>Choose one or more tags</div>
            <div className={styles.filesHeroSub}>Files are selected by tag — tag your files first if you don&apos;t see one you need.</div>

            <div className={styles.tagGridLg}>
                {fileTags.map(tag => (
                    <FileTag
                        key={tag}
                        tag={tag}
                        filter
                        size="lg"
                        active={selectedFileTags.includes(tag)}
                        count={files.filter(f => f.tags?.includes(tag)).length}
                        onClick={() => onToggleTag(tag)}
                    />
                ))}
            </div>

            <div className={styles.matchLabel}>Matched files</div>
            <div className={styles.matchList}>
                {loading && <div className={styles.matchEmpty}>Loading...</div>}
                {!loading && noTagsSelected && (
                    <div className={styles.matchEmpty}>No tags selected yet — pick a tag above.</div>
                )}
                {!loading && !noTagsSelected && matchedFiles.length === 0 && (
                    <div className={styles.matchEmpty}>No files carry the selected tags.</div>
                )}
                {!loading && matchedFiles.map(f => (
                    <div key={f.id} className={styles.matchRow}>
                        <div className={styles.matchName} title={f.name}>{f.name}</div>
                        <div className={styles.matchTagsCell}>
                            {(f.tags ?? []).map(t => <FileTag key={t} tag={t} />)}
                        </div>
                        <div className={styles.matchSize}>{formatSize(f.size)}</div>
                    </div>
                ))}
            </div>

            <div className={styles.doneRow}>
                <button type="button" className={styles.btnPrimary} style={{ flex: "none", padding: "9px 22px" }} onClick={onDone}>
                    Done
                </button>
            </div>
        </div>
    );
}
