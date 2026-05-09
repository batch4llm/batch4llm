import { useEffect, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import { ExportAPI } from "../../api/export.ts";
import { type Batch } from "../../types/Batch.ts";

export default function ExportPage() {
    const [batches, setBatches] = useState<Batch[]>([]);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [exportMode, setExportMode] = useState<string>("raw_csv");

    // Beispiel-Modi, später vom Server laden
    const exportModes = ["raw_csv", "raw_excel", "long_format_csv", "long_format_excel"];

    useEffect(() => {
        BatchesAPI.getAll().then(setBatches);
    }, []);

    const toggleSelection = (id: number) => {
        setSelectedIds(prev =>
            prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
        );
    };

    const exportSelected = async () => {
        if (selectedIds.length === 0) return;

        try {
            const response = await ExportAPI.exportBatches(exportMode, selectedIds);
            const blob = response.data;

            // Dateiname aus Header auslesen
            const contentDisposition = response.headers["content-disposition"];
            let filename = "export.csv";
            if (contentDisposition) {
                const match = contentDisposition.match(/filename="?(.+)"?/);
                if (match?.[1]) filename = match[1];
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Export failed", error);
        }
    };


    return (
        <section>
            <h2>Export Data</h2>
            <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
                <select
                    value={exportMode}
                    onChange={e => setExportMode(e.target.value)}
                >
                    {exportModes.map(mode => (
                        <option key={mode} value={mode}>
                            {mode}
                        </option>
                    ))}
                </select>
                <button onClick={exportSelected} disabled={selectedIds.length === 0}>
                    Export Selected
                </button>
            </div>
            <table>
                <thead>
                <tr>
                    <th></th>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Model</th>
                    <th>Temperature</th>
                    <th>Endpoint</th>
                    <th>File Reader</th>
                </tr>
                </thead>
                <tbody>
                {batches.map(batch => (
                    <tr key={batch.id}>
                        <td>
                            <input
                                type="checkbox"
                                checked={selectedIds.includes(batch.id)}
                                onChange={() => toggleSelection(batch.id)}
                            />
                        </td>
                        <td>{batch.id}</td>
                        <td>{batch.status}</td>
                        <td>{batch.model}</td>
                        <td>{batch.temperature}</td>
                        <td>{batch.endpoint_id}</td>
                        <td>{batch.file_reader}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </section>
    );
}
