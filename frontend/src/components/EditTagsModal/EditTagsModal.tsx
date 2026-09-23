import { useState } from "react";
import { Modal } from "../Modal/Modal";
import { TagsInput } from "../TagsInput/TagsInput";
import { FilesAPI } from "../../api/files";
import { type FileData } from "../../types/FileData";
import modalStyles from "../Modal/Modal.module.css";
import styles from "./EditTagsModal.module.css";

type Props = {
    file: FileData | null;
    onClose: () => void;
    onSaved: (file: FileData) => void;
};

export function EditTagsModal({ file, onClose, onSaved }: Props) {
    const [tags, setTags] = useState<string[]>(file?.tags ?? []);
    const [saving, setSaving] = useState(false);

    if (!file) return null;

    async function handleSave() {
        setSaving(true);
        try {
            const updated = await FilesAPI.updateTags(file!.id, tags);
            onSaved(updated);
            onClose();
        } catch (err) {
            console.error(err);
            alert(err);
        } finally {
            setSaving(false);
        }
    }

    return (
        <Modal isOpen onClose={onClose} className={styles.modal}>
            <h3 className={modalStyles.modalTitle}>Edit tags</h3>
            <p className={styles.fileName}>{file.name}</p>

            <TagsInput tags={tags} onChange={setTags} />

            <div className={styles.actions}>
                <button className={modalStyles.btnSecondary} onClick={onClose} disabled={saving}>
                    Cancel
                </button>
                <button className={styles.btnPrimary} onClick={handleSave} disabled={saving}>
                    {saving ? "Saving…" : "Save"}
                </button>
            </div>
        </Modal>
    );
}
