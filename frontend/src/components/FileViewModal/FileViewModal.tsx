import { useEffect, useState } from "react";
import { type FileData } from "../../types/FileData.ts";
import { FilesAPI } from "../../api/files.ts";
import { Modal } from "../Modal/Modal.tsx";
import { FileTag } from "../FileTag/FileTag.tsx";
import { formatBytes, formatDate, getExt } from "../../utils/fileUtils.ts";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./FileViewModal.module.css";

function IconClose() {
    return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
    );
}

function isPdf(file: FileData): boolean {
    if (file.mime_type === "application/pdf") return true;
    return file.name.split(".").pop()?.toLowerCase() === "pdf";
}

function isImage(file: FileData): boolean {
    if (file.mime_type?.startsWith("image/")) return true;
    const ext = file.name.split(".").pop()?.toLowerCase();
    return ["png", "jpg", "jpeg", "gif", "webp", "svg"].includes(ext ?? "");
}

type Props = { file: FileData | null; onClose: () => void };

export function FileViewModal({ file, onClose }: Props) {
    const [loadedId, setLoadedId] = useState<number | null>(null);
    const [url, setUrl] = useState<string | null>(null);
    const [error, setError] = useState(false);

    useEffect(() => {
        if (!file) return;
        let cancelled = false;
        FilesAPI.getUrl(file.id)
            .then(u => {
                if (!cancelled) {
                    setUrl(u);
                    setLoadedId(file.id);
                    setError(false);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setError(true);
                    setLoadedId(file.id);
                }
            });
        return () => { cancelled = true; };
    }, [file]);

    if (!file) return null;

    // Derive loading from whether the fetched ID matches the requested file
    const loading = loadedId !== file.id && !error;
    const currentUrl = loadedId === file.id ? url : null;
    const ext = getExt(file.name);

    function renderBody() {
        if (loading) return <div className={styles.stateBox}>Loading…</div>;
        if (error)   return <div className={styles.stateBox}>Could not load file.</div>;
        if (!currentUrl) return null;

        if (isPdf(file!)) {
            return (
                <div className={styles.viewer}>
                    <iframe src={currentUrl} title={file!.name} />
                </div>
            );
        }
        if (isImage(file!)) {
            return <img className={styles.viewerImage} src={currentUrl} alt={file!.name} />;
        }
        return <div className={styles.stateBox}>Preview not available for this file type.</div>;
    }

    return (
        <Modal isOpen onClose={onClose} className={styles.wideModal}>
            <div className={modalStyles.modalHeader}>
                <div className={modalStyles.modalTypeBadge}>{ext}</div>
                <div className={modalStyles.modalTitleBlock}>
                    <h3 className={modalStyles.modalTitle}>{file.name}</h3>
                    <p className={modalStyles.modalSub}>
                        {file.size != null && <span>{formatBytes(file.size)}</span>}
                        {file.size != null && file.mime_type && <span className={modalStyles.modalSep}>·</span>}
                        {file.mime_type && <span>{file.mime_type}</span>}
                        {file.created_at && (file.size != null || file.mime_type) && <span className={modalStyles.modalSep}>·</span>}
                        {file.created_at && <span>{formatDate(file.created_at)}</span>}
                    </p>
                </div>
                <button className={modalStyles.modalClose} onClick={onClose} aria-label="Close">
                    <IconClose />
                </button>
            </div>

            {(file.tags ?? []).length > 0 && (
                <div className={modalStyles.modalTags}>
                    {file.tags!.map(t => <FileTag key={t} tag={t} />)}
                </div>
            )}

            {renderBody()}

            <div className={modalStyles.modalFooter}>
                <button className={modalStyles.btnSecondary} onClick={onClose}>Close</button>
            </div>
        </Modal>
    );
}
