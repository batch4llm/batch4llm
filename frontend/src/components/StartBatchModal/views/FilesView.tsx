import type { FileData } from "../../../types/FileData";
import { FileTag } from "../../FileTag/FileTag.tsx";
import styles from "../StartBatchModal.module.css";
import { IconBack, IconSearch } from "../Icons.tsx";

type Props = {
    files: FileData[];
    loading: boolean;
    fileTags: string[];
    selectedFileTags: string[];
    selectedFileIds: number[];
    search: string;
    onSearchChange: (value: string) => void;
    onToggleTag: (tag: string) => void;
    onToggleFile: (fileId: number) => void;
    onDone: () => void;
};

function formatSize(bytes?: number): string {
    if (!bytes) return "—";
    if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    if (bytes >= 1024) return (bytes / 1024).toFixed(0) + " KB";
    return bytes + " B";
}

export function FilesView({
    files, loading, fileTags, selectedFileTags, selectedFileIds, search,
    onSearchChange, onToggleTag, onToggleFile, onDone,
}: Props) {
    const byTagIds = new Set(
        files.filter(f => selectedFileTags.some(t => f.tags?.includes(t))).map(f => f.id)
    );
    const q = search.toLowerCase();
    const filtered = files.filter(f => !q || f.name.toLowerCase().includes(q));
    const totalSelected = new Set([...byTagIds, ...selectedFileIds]).size;

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onDone}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Select Files</h2>
                {totalSelected > 0 && <span className={styles.badgeCount}>{totalSelected} selected</span>}
            </div>

            <div className={styles.sectionSublabel}>By tag</div>
            <div className={styles.tagPillWrap}>
                {fileTags.map(tag => (
                    <FileTag
                        key={tag}
                        tag={tag}
                        filter
                        active={selectedFileTags.includes(tag)}
                        onClick={() => onToggleTag(tag)}
                    />
                ))}
            </div>

            <div className={styles.orDivider}>
                <div /><span>or individual files</span><div />
            </div>

            <div className={styles.searchWrap}>
                <span className={styles.searchIcon}><IconSearch /></span>
                <input
                    type="text"
                    className={styles.searchInput}
                    placeholder="Search files..."
                    value={search}
                    onChange={(e) => onSearchChange(e.target.value)}
                />
            </div>

            <div className={styles.fileTable}>
                <div className={styles.fileTableHead}>
                    <div />
                    <span>Name</span>
                    <span>Size</span>
                    <span>Tags</span>
                </div>
                <div className={styles.fileTableBody}>
                    {loading && <div className={styles.emptyNote}>Loading...</div>}
                    {!loading && filtered.length === 0 && <div className={styles.emptyNote}>No files found.</div>}
                    {filtered.map((f) => {
                        const byTag = byTagIds.has(f.id);
                        const byDirect = selectedFileIds.includes(f.id);
                        const checked = byTag || byDirect;
                        return (
                            <div key={f.id} className={`${styles.fileRow}${checked ? ` ${styles.checked}` : ""}`}>
                                <input
                                    type="checkbox"
                                    checked={checked}
                                    disabled={byTag}
                                    title={byTag ? "Selected via tag" : undefined}
                                    onChange={() => onToggleFile(f.id)}
                                />
                                <div className={styles.fileName} title={f.name}>{f.name}</div>
                                <div className={styles.fileSize}>{formatSize(f.size)}</div>
                                <div className={styles.fileTagsCell}>
                                    {(f.tags ?? []).map(t => <FileTag key={t} tag={t} />)}
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className={styles.doneRow}>
                <button type="button" className={styles.btnPrimary} style={{ flex: "none", padding: "9px 22px" }} onClick={onDone}>
                    Done
                </button>
            </div>
        </div>
    );
}
