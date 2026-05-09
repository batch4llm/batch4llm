import { type FileData } from "../../types/FileData.ts";
import { Modal } from "../Modal/Modal.tsx";
import { FileTag } from "../FileTag/FileTag.tsx";
import { getExt } from "../../utils/fileUtils.ts";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./ReaderTestModal.module.css";

function IconClose() {
    return (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M6 6l12 12M18 6L6 18"/>
        </svg>
    );
}

type Props = { file: FileData | null; onClose: () => void };

export function ReaderTestModal({ file, onClose }: Props) {
    if (!file) return null;
    const ext = getExt(file.name);
    return (
        <Modal isOpen onClose={onClose} className={styles.narrowModal}>
            <div className={modalStyles.modalHeader}>
                <div className={modalStyles.modalTypeBadge}>{ext}</div>
                <div className={modalStyles.modalTitleBlock}>
                    <h3 className={modalStyles.modalTitle}>Test file reader</h3>
                    <p className={modalStyles.modalSub}>
                        <span>{file.name}</span>
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

            <div className={styles.placeholderBody}>
                File reader test coming soon.
            </div>

            <div className={modalStyles.modalFooter}>
                <button className={modalStyles.btnSecondary} onClick={onClose}>Close</button>
            </div>
        </Modal>
    );
}
