import { useEffect, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import { type Batch, ACTIVE_STATUSES } from "../../types/Batch.ts";
import { type BatchFile } from "../../types/BatchFile.ts";
import { Button } from "../../components/Button/Button.tsx";
import { StartBatchModal } from "../../components/StartBatchModal/StartBatchModal.tsx";
import { BatchLogModal } from "../../components/BatchLogModal/BatchLogModal.tsx";
import { BatchStatusSymbol } from "../../components/BatchStatusSymbol/BatchStatusSymbol.tsx";
import { BatchTimer } from "../../components/BatchTimer/BatchTimer.tsx";
import { BatchDetailModal } from "../../components/BatchDetailModal/BatchDetailModal.tsx";
import { EndpointModal } from "../../components/EndpointModal/EndpointModal.tsx";
import { PromptModal } from "../../components/PromptModal/PromptModal.tsx";
import styles from "./BatchesPage.module.css";

export default function BatchesPage() {
    const [batches, setBatches] = useState<Batch[]>([]);
    const [batchFiles, setBatchFiles] = useState<Record<number, BatchFile[]>>({});

    const [isStartModalOpen, setIsStartModalOpen] = useState(false);

    const [logBatchId, setLogBatchId] = useState<number | null>(null);
    const [detailBatchId, setDetailBatchId] = useState<number | null>(null);
    const [endpointBatchId, setEndpointBatchId] = useState<number | null>(null);
    const [promptBatchId, setPromptBatchId] = useState<number | null>(null);

    // ── Initial load ──────────────────────────────────────────────────────────
    useEffect(() => {
        BatchesAPI.getAll().then(setBatches);
    }, []);

    // ── Auto-refresh while any batch is active ────────────────────────────────
    useEffect(() => {
        const hasActiveBatch = batches.some(b => ACTIVE_STATUSES.includes(b.status));
        if (!hasActiveBatch) return;

        const interval = setInterval(() => {
            BatchesAPI.getAll().then(setBatches);
        }, 5000);

        return () => clearInterval(interval);
    }, [batches]);

    // ── Auto-refresh files for open detail modal ──────────────────────────────
    useEffect(() => {
        if (!detailBatchId) return;
        const expandedBatch = batches.find(b => b.id === detailBatchId);
        if (!expandedBatch || !ACTIVE_STATUSES.includes(expandedBatch.status)) return;

        const interval = setInterval(() => {
            BatchesAPI.getBatchFilesById(detailBatchId).then(files =>
                setBatchFiles(prev => ({ ...prev, [detailBatchId]: files }))
            );
        }, 5000);

        return () => clearInterval(interval);
    }, [batches, detailBatchId]);

    // ── Actions ───────────────────────────────────────────────────────────────
    function handleStop(e: React.MouseEvent, batch_id: number) {
        e.stopPropagation();
        BatchesAPI.stop(batch_id).catch(err => {
            alert(err);
            console.error(err);
        });
    }

    function openDetail(e: React.MouseEvent | null, batch: Batch) {
        if (e) e.stopPropagation();
        if (!batchFiles[batch.id]) {
            BatchesAPI.getBatchFilesById(batch.id).then(files =>
                setBatchFiles(prev => ({ ...prev, [batch.id]: files }))
            );
        }
        setDetailBatchId(batch.id);
    }

    const logBatch    = batches.find(b => b.id === logBatchId)    ?? null;
    const detailBatch = batches.find(b => b.id === detailBatchId) ?? null;
    const endpointBatch = batches.find(b => b.id === endpointBatchId) ?? null;
    const promptBatch   = batches.find(b => b.id === promptBatchId)   ?? null;

    return (
        <section className={styles.page}>
            <h2 className={styles.heading}>Batch Runs</h2>

            <div className={styles.batchList}>
                {batches.map(batch => (
                    <div
                        key={batch.id}
                        className={styles.batchCard}
                        onClick={e => openDetail(e, batch)}
                        role="button"
                        tabIndex={0}
                        onKeyDown={e => e.key === "Enter" && openDetail(null, batch)}
                    >
                        {/* ── Top row: meta chips ─────────────────────────── */}
                        <div className={styles.cardTop}>
                            <span className={styles.batchId}>#{batch.id}</span>

                            <BatchStatusSymbol status={batch.status} />


                            <span className={styles.model}>{batch.model}</span>
                        </div>

                        {/* ── Middle row: progress + time ─────────────────── */}
                        <div className={styles.cardMid}>
                            <div className={styles.progressWrap}>
                                <span className={styles.progressLabel}>Progress</span>
                                <span className={styles.progressValue}>{batch.progress}</span>
                            </div>

                            <div className={styles.timerWrap}>
                                <span className={styles.progressLabel}>Time</span>
                                {batch.started_at
                                    ? <BatchTimer startTime={batch.started_at} stopTime={batch.stopped_at} />
                                    : <span className={styles.progressValue}>—</span>
                                }
                            </div>

                            {batch.costs_in_usd && batch.costs_in_usd > 0 && (
                                <div className={styles.costsWrap}>
                                    <span className={styles.progressLabel}>Costs</span>
                                    <span className={styles.progressValue}>${batch.costs_in_usd.toFixed(4)}</span>
                                </div>
                            )}
                        </div>

                        {/* ── Bottom row: action buttons ───────────────────── */}
                        <div className={styles.cardActions}>
                            {/* Front actions */}
                            <div className={styles.cardActionsLeft}>
                                <button
                                    className={styles.iconBtn}
                                    onClick={e => { e.stopPropagation(); setLogBatchId(batch.id); }}
                                    title="View log"
                                >
                                    <LogIcon /> Log
                                </button>
                                <button
                                    className={styles.iconBtn}
                                    onClick={e => openDetail(e, batch)}
                                    title="View details"
                                >
                                    <DetailIcon /> Details
                                </button>
                                {/* Clickable endpoint chip */}
                                <button
                                    className={styles.chip}
                                    onClick={e => { e.stopPropagation(); setEndpointBatchId(batch.id); }}
                                    title="View endpoint"
                                >
                                    <span className={styles.chipLabel}>Endpoint</span>
                                    <span className={styles.chipValue}>{batch.endpoint_name ?? batch.endpoint_id}</span>
                                </button>

                                {/* Clickable prompt chip */}
                                <button
                                    className={styles.chip}
                                    onClick={e => { e.stopPropagation(); setPromptBatchId(batch.id); }}
                                    title="View prompt"
                                >
                                    <span className={styles.chipLabel}>Prompt</span>
                                    <span className={styles.chipValue}>{batch.prompt_name ?? batch.prompt_id}</span>
                                </button>
                            </div>

                            {batch.status === "RUNNING" && (
                                <button
                                    className={`${styles.iconBtn} ${styles.stopBtn}`}
                                    onClick={e => handleStop(e, batch.id)}
                                    title="Stop batch"
                                >
                                    <StopIcon /> Stop
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* ── Start button ─────────────────────────────────────────────── */}
            <div className={styles.startWrap}>
                <Button text="Start Batch" onClick={() => setIsStartModalOpen(true)} />
            </div>

            {/* ── Modals ───────────────────────────────────────────────────── */}
            <StartBatchModal
                isOpen={isStartModalOpen}
                onClose={() => setIsStartModalOpen(false)}
                onCreated={(newBatch: Batch) => setBatches(prev => [...prev, newBatch])}
            />

            {logBatch && (
                <BatchLogModal
                    isOpen={!!logBatchId}
                    onClose={() => setLogBatchId(null)}
                    batch={logBatch}
                />
            )}

            {detailBatch && (
                <BatchDetailModal
                    isOpen={!!detailBatchId}
                    onClose={() => setDetailBatchId(null)}
                    files={batchFiles[detailBatch.id] ?? []}
                />
            )}

            {endpointBatch && (
                <EndpointModal
                    isOpen={!!endpointBatchId}
                    onClose={() => setEndpointBatchId(null)}
                />
            )}

            {promptBatch && (
                <PromptModal
                    isOpen={!!promptBatchId}
                    onClose={() => setPromptBatchId(null)}
                />
            )}
        </section>
    );
}

// ── Inline micro-icons (no extra dep needed) ──────────────────────────────────
function LogIcon() {
    return (
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <line x1="2" y1="4" x2="14" y2="4" />
            <line x1="2" y1="8" x2="14" y2="8" />
            <line x1="2" y1="12" x2="9"  y2="12" />
        </svg>
    );
}

function DetailIcon() {
    return (
        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="2" width="12" height="12" rx="2" />
            <line x1="5" y1="8" x2="11" y2="8" />
            <line x1="8" y1="5" x2="8"  y2="11" />
        </svg>
    );
}

function StopIcon() {
    return (
        <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor">
            <rect x="3" y="3" width="10" height="10" rx="1.5" />
        </svg>
    );
}