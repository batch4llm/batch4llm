import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { ExportAPI } from "../../api/export.ts";
import type { Batch } from "../../types/Batch.ts";
import styles from "./ExportModal.module.css";

const EXPORT_MODES = [
    { value: "raw_csv",           label: "Raw CSV" },
    { value: "raw_excel",         label: "Raw Excel" },
    { value: "long_format_csv",   label: "Long Format CSV" },
    { value: "long_format_excel", label: "Long Format Excel" },
];

type Props = {
    isOpen: boolean;
    onClose: () => void;
    batch: Batch;
};

export function ExportModal({ isOpen, onClose, batch }: Props) {
    const [mode, setMode] = useState("raw_csv");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleExport() {
        setLoading(true);
        setError(null);
        try {
            const res = await ExportAPI.exportBatches(mode, [batch.id]);
            const contentDisposition = res.headers["content-disposition"];
            let filename = `batch-${batch.id}.${mode.includes("excel") ? "xlsx" : "csv"}`;
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?([^"]+)"?/);
                if (match?.[1]) filename = match[1];
            }
            const url = URL.createObjectURL(res.data);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
            onClose();
        } catch (err) {
            setError("Export failed. Please try again.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <div className={styles.container}>
                <h3 className={styles.title}>Export Batch #{batch.id}</h3>
                <p className={styles.sub}>{batch.model}</p>

                <label className={styles.label}>Export format</label>
                <select
                    className={styles.select}
                    value={mode}
                    onChange={e => setMode(e.target.value)}
                    disabled={loading}
                >
                    {EXPORT_MODES.map(m => (
                        <option key={m.value} value={m.value}>{m.label}</option>
                    ))}
                </select>

                {error && <p className={styles.error}>{error}</p>}

                <div className={styles.footer}>
                    <button className={styles.btnCancel} onClick={onClose} disabled={loading}>
                        Cancel
                    </button>
                    <button className={styles.btnExport} onClick={handleExport} disabled={loading}>
                        {loading ? "Exporting…" : "Export"}
                    </button>
                </div>
            </div>
        </Modal>
    );
}
