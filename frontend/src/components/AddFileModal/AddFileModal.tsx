import { useCallback, useRef, useState } from "react";
import { Modal } from "../Modal/Modal";
import { FilesAPI } from "../../api/files";
import styles from "./AddFileModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onUploaded: (success: boolean) => void;
};

export function AddFileModal({ isOpen, onClose, onUploaded }: Props) {
    const [files, setFiles] = useState<File[]>(() => isOpen ? [] : []);
    const [tag, setTag] = useState(() => isOpen ? "" : "");
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [inputKey, setInputKey] = useState(0);


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
        addFiles(e.dataTransfer.files);
    }

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
        e.preventDefault();

        try {
            for (const file of files) {
                await FilesAPI.upload(file, tag ? [tag] : undefined);
            }
            onUploaded(true);
            onClose();
        } catch (err) {
            console.error(err);
            alert(err);
            onUploaded(false);
        }
    };


    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Add Files</h3>

            {/* Dropzone */}
            <div
                className={styles.dropzone}
                onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                }}
                onDragOver={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                }}
                onDrop={(e) => {
                    e.stopPropagation();
                    handleDrop(e);
                }}
            >
                Click or drop files here
                <input
                    key={inputKey}
                    ref={fileInputRef}
                    type="file"
                    multiple
                    hidden
                    onChange={handleFileInput}
                />

            </div>

            {/* Selected files */}
            {files.length > 0 && (
                <ul className={styles.fileList}>
                    {files.map((f, i) => (
                        <li key={`${f.name}-${i}`}>{f.name}</li>
                    ))}
                </ul>
            )}

            <form onSubmit={handleSubmit} className={styles.form}>
                <input
                    type="text"
                    placeholder="Tag (optional)"
                    value={tag}
                    onChange={(e) => setTag(e.target.value)}
                />

                <button type="submit" disabled={files.length === 0}>
                    Upload
                </button>
            </form>
        </Modal>
    );
}
