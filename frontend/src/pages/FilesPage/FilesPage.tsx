import { useEffect, useState } from "react";
import { FilesAPI } from "../../api/files.ts";
import { type FileData } from "../../types/FileData.ts";
import { formatBytes, formatDate } from "../../utils/fileUtils.ts";
import { FileTag } from "../../components/FileTag/FileTag.tsx";
import { FileViewModal } from "../../components/FileViewModal/FileViewModal.tsx";
import { ReaderTestModal } from "../../components/ReaderTestModal/ReaderTestModal.tsx";
import { AddFileModal } from "../../components/AddFileModal/AddFileModal.tsx";
import { Modal } from "../../components/Modal/Modal.tsx";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import styles from "./FilesPage.module.css";

// ── Icons (FilesPage-only) ────────────────────────────────────
function IconEye() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/>
            <circle cx="12" cy="12" r="3"/>
        </svg>
    );
}

function IconBeaker() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 3h6"/>
            <path d="M10 3v6L4.5 18.5A2 2 0 0 0 6.2 21.5h11.6a2 2 0 0 0 1.7-3L14 9V3"/>
            <path d="M7 14h10"/>
        </svg>
    );
}

function IconTrash() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 6h18"/>
            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            <path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>
            <path d="M10 11v6M14 11v6"/>
        </svg>
    );
}

function IconSearch() {
    return (
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="7"/>
            <path d="M20 20l-3.5-3.5"/>
        </svg>
    );
}

// ── Confirm Delete Modal (file-specific, stays here) ──────────
type DeleteModalProps = {
    file: FileData | null;
    onClose: () => void;
    onConfirm: (id: number) => void;
};

function ConfirmDeleteModal({ file, onClose, onConfirm }: DeleteModalProps) {
    if (!file) return null;
    return (
        <Modal isOpen onClose={onClose} className={styles.narrowModal}>
            <h3 className={styles.confirmTitle}>Delete file?</h3>
            <p className={styles.confirmBody}>
                <strong>{file.name}</strong> will be permanently removed from your workspace.
                This cannot be undone.
            </p>
            <div className={styles.confirmActions}>
                <button className={styles.btnSecondary} onClick={onClose}>Cancel</button>
                <button className={styles.btnDanger} onClick={() => { onConfirm(file.id); onClose(); }}>Delete</button>
            </div>
        </Modal>
    );
}

// ── Page ──────────────────────────────────────────────────────
export default function FilesPage() {
    const [files, setFiles] = useState<FileData[]>([]);
    const [query, setQuery] = useState("");
    const [activeTags, setActiveTags] = useState<string[]>([]);
    const [isUploadOpen, setIsUploadOpen] = useState(false);
    const [uploadKey, setUploadKey] = useState(0);
    const [viewing, setViewing] = useState<FileData | null>(null);
    const [testing, setTesting] = useState<FileData | null>(null);
    const [deleting, setDeleting] = useState<FileData | null>(null);

    function loadFiles() {
        FilesAPI.getAll().then(setFiles);
    }

    useEffect(() => { loadFiles(); }, []);

    const allTagIds = Array.from(new Set(files.flatMap(f => f.tags ?? [])));

    function toggleTag(id: string) {
        setActiveTags(prev => prev.includes(id) ? prev.filter(t => t !== id) : [...prev, id]);
    }

    const filtered = files.filter(f => {
        const matchesQuery = !query || f.name.toLowerCase().includes(query.toLowerCase());
        const matchesTags = activeTags.length === 0 || activeTags.some(t => (f.tags ?? []).includes(t));
        return matchesQuery && matchesTags;
    });

    const totalSize = filtered.reduce((acc, f) => acc + (f.size ?? 0), 0);

    function handleDelete(id: number) {
        FilesAPI.delete(id).then(() => setFiles(prev => prev.filter(f => f.id !== id)));
    }

    return (
        <section>
            <PageHeader
                title="Files"
                subtitle="Source files available to batches. Tag them by purpose to find them faster."
                count={files.length}
                addLabel="Upload File"
                onAdd={() => { setUploadKey(k => k + 1); setIsUploadOpen(true); }}
            />

            <div className={styles.toolbar}>
                <div className={styles.search}>
                    <span className={styles.searchIcon}><IconSearch /></span>
                    <input
                        className={styles.searchInput}
                        type="search"
                        placeholder="Search files…"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                </div>
                {allTagIds.length > 0 && (
                    <div className={styles.tagFilterRow}>
                        <span className={styles.tagFilterLabel}>Filter:</span>
                        {allTagIds.map(id => (
                            <FileTag
                                key={id}
                                tag={id}
                                filter
                                active={activeTags.length === 0 || activeTags.includes(id)}
                                onClick={() => toggleTag(id)}
                            />
                        ))}
                    </div>
                )}
            </div>

            <div className={styles.list}>
                <div className={styles.listHead}>
                    <div>Name</div>
                    <div>Type</div>
                    <div>Size</div>
                    <div>Tags</div>
                    <div className={styles.listHeadActions}>Actions</div>
                </div>

                {filtered.length === 0 && (
                    <div className={styles.empty}>No files match your search.</div>
                )}

                {filtered.map(f => (
                    <div key={f.id} className={styles.row}>
                        <div className={styles.rowName}>
                            <span className={styles.rowNameText}>{f.name}</span>
                            {f.created_at && (
                                <span className={styles.rowNameMeta}>Added {formatDate(f.created_at)}</span>
                            )}
                        </div>
                        <div className={styles.rowExt}>.{f.name.split(".").pop()?.toLowerCase() ?? "?"}</div>
                        <div className={styles.rowSize}>{f.size != null ? formatBytes(f.size) : "—"}</div>
                        <div className={styles.rowTags}>
                            {(f.tags ?? []).map(t => <FileTag key={t} tag={t} />)}
                        </div>
                        <div className={styles.rowActions}>
                            <button className={styles.iconBtn} title="View file" onClick={() => setViewing(f)}>
                                <IconEye />
                            </button>
                            <button className={styles.iconBtn} title="Test file reader" onClick={() => setTesting(f)}>
                                <IconBeaker />
                            </button>
                            <button
                                className={`${styles.iconBtn} ${styles.iconBtnDanger}`}
                                title="Delete file"
                                onClick={() => setDeleting(f)}
                            >
                                <IconTrash />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className={styles.foot}>
                <span>{filtered.length} of {files.length} file{files.length === 1 ? "" : "s"}</span>
                <span>{formatBytes(totalSize)} shown</span>
            </div>

            <AddFileModal
                key={uploadKey}
                isOpen={isUploadOpen}
                onClose={() => setIsUploadOpen(false)}
                onUploaded={() => loadFiles()}
            />

            <FileViewModal file={viewing} onClose={() => setViewing(null)} />
            <ReaderTestModal file={testing} onClose={() => setTesting(null)} />
            <ConfirmDeleteModal file={deleting} onClose={() => setDeleting(null)} onConfirm={handleDelete} />
        </section>
    );
}
