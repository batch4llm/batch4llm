import { useCallback, useRef, useState } from "react";
import { Modal } from "../Modal/Modal";
import { FilesAPI } from "../../api/files";
import { TagsInput } from "../TagsInput/TagsInput";
import { IconUpload, IconFile, IconWarning } from "./Icons";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./AddFileModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onUploaded: (success: boolean) => void;
};

function formatSize(bytes: number): string {
    if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    if (bytes >= 1024) return (bytes / 1024).toFixed(0) + " KB";
    return bytes + " B";
}

export function AddFileModal({ isOpen, onClose, onUploaded }: Props) {
    const [files, setFiles] = useState<File[]>([]);
    const [tags, setTags] = useState<string[]>([]);
    const [dragOver, setDragOver] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [showTagWarning, setShowTagWarning] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [inputKey, setInputKey] = useState(0);

    // Reset the form whenever the modal is (re-)opened.
    const [wasOpen, setWasOpen] = useState(isOpen);
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) {
            setFiles([]);
            setTags([]);
            setUploading(false);
            setShowTagWarning(false);
        }
    }

    const addFiles = useCallback((newFiles: FileList | File[]) => {
        setFiles(prev => [...prev, ...Array.from(newFiles)]);
    }, []);

    function handleFileInput(e: React.ChangeEvent<HTMLInputElement>) {
        if (!e.target.files) return;
        addFiles(e.target.files);
        // Reset input by changing key
        setInputKey(prev => prev + 1);
    }

    function handleDrop(e: React.DragEvent<HTMLDivElement>) {
        e.preventDefault();
        setDragOver(false);
        addFiles(e.dataTransfer.files);
    }

    function removeFile(index: number) {
        setFiles(prev => prev.filter((_, i) => i !== index));
    }

    const doUpload = async (): Promise<void> => {
        setUploading(true);
        try {
            for (const file of files) {
                await FilesAPI.upload(file, tags.length > 0 ? tags : undefined);
            }
            onUploaded(true);
            onClose();
        } catch (err) {
            console.error(err);
            alert(err);
            onUploaded(false);
        } finally {
            setUploading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();
        if (files.length === 0 || uploading) return;

        // Tags make files much easier to find and batch together later — nudge
        // the user to add one before letting an untagged upload through.
        if (tags.length === 0 && !showTagWarning) {
            setShowTagWarning(true);
            return;
        }

        await doUpload();
    };

    return (
        <Modal isOpen={isOpen} onClose={uploading ? () => {} : onClose} className={styles.modal}>
            <div className={styles.view}>
                <div className={styles.viewHeader}>
                    <h3 className={styles.viewTitle}>Add Files</h3>
                    {files.length > 0 && <span className={styles.badgeCount}>{files.length} selected</span>}
                </div>

                <div
                    className={`${styles.dropzone} ${dragOver ? styles.dragOver : ""}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        fileInputRef.current?.click();
                    }}
                    onDragOver={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setDragOver(true);
                    }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={(e) => {
                        e.stopPropagation();
                        handleDrop(e);
                    }}
                >
                    <IconUpload />
                    <div className={styles.dropzoneText}>Click to browse or drag files here</div>
                    <div className={styles.dropzoneHint}>Any file type &middot; multiple files supported</div>
                    <input
                        key={inputKey}
                        ref={fileInputRef}
                        type="file"
                        multiple
                        hidden
                        onChange={handleFileInput}
                    />
                </div>

                {files.length > 0 && (
                    <div className={styles.fileListWrap}>
                        <div className={styles.fileListHeader}>
                            <span className={styles.fileListLabel}>Files to upload</span>
                            <button type="button" className={styles.clearAllBtn} onClick={() => setFiles([])}>
                                Clear all
                            </button>
                        </div>
                        <div className={styles.fileList}>
                            {files.map((f, i) => (
                                <div key={`${f.name}-${i}`} className={styles.fileRow}>
                                    <span className={styles.fileIcon}><IconFile /></span>
                                    <span className={styles.fileName} title={f.name}>{f.name}</span>
                                    <span className={styles.fileSize}>{formatSize(f.size)}</span>
                                    <button
                                        type="button"
                                        className={styles.fileRemove}
                                        onClick={() => removeFile(i)}
                                        aria-label={`Remove ${f.name}`}
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.fieldGroup}>
                        <span className={styles.label}>
                            Tags
                            <span className={styles.recommendedBadge}>Strongly recommended</span>
                        </span>
                        <TagsInput
                            tags={tags}
                            onChange={(next) => { setTags(next); if (next.length > 0) setShowTagWarning(false); }}
                            placeholder="Add a tag, e.g. test-set, eval-batch…"
                        />
                    </div>

                    {showTagWarning && tags.length === 0 && (
                        <div className={styles.warnBox}>
                            <div className={styles.warnBoxTitle}>
                                <IconWarning /> No tags added
                            </div>
                            <p className={styles.warnBoxMessage}>
                                Without a tag, these files will be harder to find and select together later
                                (e.g. when starting a batch). We strongly recommend adding at least one tag.
                            </p>
                            <div className={styles.warnBoxActions}>
                                <button type="button" className={styles.warnBtnGhost} onClick={() => setShowTagWarning(false)}>
                                    Add a tag
                                </button>
                                <button type="button" className={styles.warnBtnSolid} onClick={doUpload} disabled={uploading}>
                                    Upload without tags
                                </button>
                            </div>
                        </div>
                    )}

                    <div className={styles.footer}>
                        <button type="button" className={modalStyles.btnSecondary} onClick={onClose} disabled={uploading}>
                            Cancel
                        </button>
                        <button type="submit" className={styles.btnPrimary} disabled={files.length === 0 || uploading}>
                            {uploading ? "Uploading…" : `Upload${files.length > 0 ? ` ${files.length} file${files.length > 1 ? "s" : ""}` : ""}`}
                        </button>
                    </div>
                </form>
            </div>
        </Modal>
    );
}
