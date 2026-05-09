import { type BatchFile } from "../../types/BatchFile.ts";
import styles from "./BatchDetailView.module.css";
import {useState} from "react";
import {BatchFileModal} from "../BatchFileModal/BatchFileModal.tsx";
import {Modal} from "../Modal/Modal.tsx";

interface BatchDetailViewProps {
    isOpen: boolean;
    onClose: () => void;
    files: BatchFile[];
}

export function BatchDetailModal({isOpen, onClose, files }: BatchDetailViewProps) {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalFile, setModalFile] = useState<BatchFile | null>(null);


    const getStatusStyle = (status: BatchFile["status"]) => {
        switch (status) {
            case "COMPLETED":
                return { backgroundColor: "#e6f7e6", symbol: "✓" };
            case "FAILED":
                return { backgroundColor: "#ffe6e6", symbol: "✗" };
            case "RUNNING":
                return { backgroundColor: "#e6f0ff", symbol: "→" };
            case "QUEUED":
            default:
                return { backgroundColor: "#f5f5f5", symbol: "•" };
        }
    };

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <section>
                <div className={styles.batchDetails}>
                    <h4>Batch Files:</h4>
                    <div className={styles.batchFilesList}>
                        {files.map((file) => {
                            const { backgroundColor, symbol } = getStatusStyle(file.status);
                            return (
                                <div
                                    key={file.id}
                                    className={styles.batchFileItem}
                                    style={{ backgroundColor }}
                                    onClick={() => {setModalFile(file); setIsModalOpen(true)}}
                                >
                                    <div>{file.name}</div>
                                    {file.costs_in_usd && <div>${file.costs_in_usd.toFixed(4)}</div>}
                                    <div className={styles.statusContainer}>
                                        <span>{file.status}</span>
                                        <span className={styles.statusSymbol}>{symbol}</span>
                                    </div>

                                </div>
                            );
                        })}
                    </div>

                </div>
                {isModalOpen && modalFile && (
                    <BatchFileModal
                        isOpen={isModalOpen}
                        onClose={() => setIsModalOpen(false)}
                        file={modalFile}
                    />
                )}
            </section>
        </Modal>
    );
}
