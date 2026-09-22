import { useEffect, useMemo, useState } from "react";
import { BatchesAPI } from "../../api/batches.ts";
import { PromptsAPI } from "../../api/prompts.ts";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { type Batch, type BatchStatus, ACTIVE_STATUSES } from "../../types/Batch.ts";
import { type Prompt } from "../../types/Prompt.ts";
import { type Endpoint } from "../../types/Endpoint.ts";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import { StartBatchModal } from "../../components/StartBatchModal/StartBatchModal.tsx";
import { BatchLogModal } from "../../components/BatchLogModal/BatchLogModal.tsx";
import { BatchTimer } from "../../components/BatchTimer/BatchTimer.tsx";
import { BatchDetailModal } from "../../components/BatchDetailModal/BatchDetailModal.tsx";
import { EndpointModal } from "../../components/EndpointModal/EndpointModal.tsx";
import { PromptModal } from "../../components/PromptModal/PromptModal.tsx";
import { AddPromptModal } from "../../components/AddPromptModal/AddPromptModal.tsx";
import { ExportModal } from "../../components/ExportModal/ExportModal.tsx";
import styles from "./BatchesPage.module.css";

type Tab = "batches" | "archived";

// ── Status helpers ────────────────────────────────────────────────────────────
const STATUS_LABEL: Record<BatchStatus, string> = {
    SCHEDULED:              "scheduled",
    QUEUED:                 "queued",
    RUNNING:                "running",
    PROVIDER_BATCH_PENDING: "pending",
    COMPLETED:              "completed",
    STOPPED:                "stopped",
    FAILED:                 "failed",
};

const STATUS_CLASS: Record<BatchStatus, string> = {
    SCHEDULED:              styles.statusQueued,
    QUEUED:                 styles.statusQueued,
    RUNNING:                styles.statusRunning,
    PROVIDER_BATCH_PENDING: styles.statusPending,
    COMPLETED:              styles.statusCompleted,
    STOPPED:                styles.statusStopped,
    FAILED:                 styles.statusFailed,
};

function parsePct(progress?: string): number {
    if (!progress) return 0;
    const [done, total] = progress.split("/").map(Number);
    if (!total || isNaN(done) || isNaN(total)) return 0;
    return Math.min(100, Math.round((done / total) * 100));
}

const ACTIVE_STATUS_ORDER: Record<BatchStatus, number> = {
    SCHEDULED:              0,
    QUEUED:                 1,
    RUNNING:                2,
    PROVIDER_BATCH_PENDING: 3,
    COMPLETED:              4,
    STOPPED:                4,
    FAILED:                 4,
};

function sortActive(batches: Batch[]): Batch[] {
    return [...batches].sort((a, b) =>
        ACTIVE_STATUS_ORDER[a.status] - ACTIVE_STATUS_ORDER[b.status] ||
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
}

function sortHistory(batches: Batch[]): Batch[] {
    return [...batches].sort((a, b) =>
        new Date(b.stopped_at ?? b.updated_at).getTime() - new Date(a.stopped_at ?? a.updated_at).getTime()
    );
}

function matchSearch(batch: Batch, q: string): boolean {
    if (!q) return true;
    const lower = q.toLowerCase();
    return (
        batch.name.toLowerCase().includes(lower) ||
        String(batch.id).includes(lower) ||
        batch.model.toLowerCase().includes(lower) ||
        (batch.endpoint_name ?? String(batch.endpoint_id ?? "")).toLowerCase().includes(lower) ||
        (batch.prompt_name ?? String(batch.prompt_id ?? "")).toLowerCase().includes(lower)
    );
}

// ── BatchCard ─────────────────────────────────────────────────────────────────
interface BatchCardProps {
    batch: Batch;
    isExpanded: boolean;
    onToggleExpanded: (b: Batch) => void;
    onDetails: (b: Batch) => void;
    onLog: (b: Batch) => void;
    onExport: (b: Batch) => void;
    onStop: (b: Batch) => Promise<void>;
    onArchive: (b: Batch) => void;
}

function BatchCard({ batch, isExpanded, onToggleExpanded, onDetails, onLog, onExport, onStop, onArchive }: BatchCardProps) {
    const [isStopping, setIsStopping] = useState(false);
    const isActive = ACTIVE_STATUSES.includes(batch.status);
    const isRunning = batch.status === "RUNNING";
    const isQueued  = batch.status === "QUEUED" || batch.status === "SCHEDULED";
    const isPending = batch.status === "PROVIDER_BATCH_PENDING";
    const isArchived = !!batch.archived_at;
    const pct = parsePct(batch.progress);

    function stop(fn: (b: Batch) => void) {
        return (e: React.MouseEvent) => { e.stopPropagation(); fn(batch); };
    }

    function toggleExpanded() {
        onToggleExpanded(batch);
    }

    function handleStopClick(e: React.MouseEvent) {
        e.stopPropagation();
        if (isStopping) return;
        setIsStopping(true);
        onStop(batch).finally(() => setIsStopping(false));
    }

    return (
        <div
            className={`${styles.card} ${STATUS_CLASS[batch.status]}${isArchived ? ` ${styles.isArchived}` : ""}${isExpanded ? ` ${styles.isExpanded}` : ""}`}
            role="button"
            tabIndex={0}
            aria-expanded={isExpanded}
            onClick={toggleExpanded}
            onKeyDown={e => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), toggleExpanded())}
        >
            {/* ── Title row ──────────────────────────────────────── */}
            <div className={styles.cardTop}>
                <span className={styles.name}>{batch.name}</span>
                <span className={styles.statusWord}>{STATUS_LABEL[batch.status]}</span>
                <IcChevron className={styles.chevron} />
            </div>

            {/* ── Sub-meta ───────────────────────────────────────── */}
            <div className={styles.sub}>
                <span className={styles.batchId}>#{batch.id}</span>
                <span className={styles.sep}>·</span>
                <span>{batch.model}</span>
                <span className={styles.sep}>·</span>
                {batch.endpoint_id != null ? (
                    <span className={styles.metaText}>
                        {batch.endpoint_name ?? `endpoint #${batch.endpoint_id}`}
                    </span>
                ) : (
                    <span className={styles.metaTextDeleted} title="Endpoint was deleted">
                        {batch.endpoint_name ?? "endpoint deleted"}
                    </span>
                )}
                <span className={styles.sep}>·</span>
                {batch.prompt_id != null ? (
                    <span className={styles.metaText}>
                        {batch.prompt_name ?? `prompt #${batch.prompt_id}`}
                    </span>
                ) : (
                    <span className={styles.metaTextDeleted} title="Prompt was deleted">
                        {batch.prompt_name ?? "prompt deleted"}
                    </span>
                )}
            </div>

            {/* ── Stats row ──────────────────────────────────────── */}
            <div className={styles.stats}>
                {batch.progress && (
                    <div className={styles.stat}>
                        <span className={styles.statKey}>Progress</span>
                        <span className={styles.statMono}>{batch.progress}</span>
                        <span className={styles.statMuted}>· {pct}%</span>
                    </div>
                )}
                {batch.started_at && (
                    <div className={styles.stat}>
                        <span className={styles.statKey}>Time</span>
                        <span className={`${styles.statMono}${isRunning ? ` ${styles.liveTimer}` : ""}`}>
                            <BatchTimer startTime={batch.started_at} stopTime={batch.stopped_at} />
                        </span>
                    </div>
                )}
                {batch.costs_in_usd != null && batch.costs_in_usd > 0 && (
                    <div className={styles.stat}>
                        <span className={styles.statKey}>Cost</span>
                        <span className={styles.statMono}>${batch.costs_in_usd.toFixed(4)}</span>
                    </div>
                )}
            </div>

            {/* ── Progress bar ───────────────────────────────────── */}
            <div className={`${styles.bar}${isQueued ? ` ${styles.barQueued}` : isPending ? ` ${styles.barPending}` : ""}`}>
                {!isQueued && !isPending && <span style={{ width: `${pct}%` }} />}
            </div>

            {/* ── Action panel (revealed when card is expanded) ───── */}
            {isExpanded && (
                <div className={styles.actionsPanel} onClick={e => e.stopPropagation()}>
                    <button className={styles.actionBtn} onClick={stop(onDetails)}>
                        <IcDetails /> View details
                    </button>
                    <button className={styles.actionBtn} onClick={stop(onLog)}>
                        <IcLog /> View log
                    </button>
                    <button className={styles.actionBtn} onClick={stop(onExport)}>
                        <IcExport /> Export
                    </button>
                    {isActive && (
                        <button
                            className={`${styles.actionBtn} ${styles.actionBtnStop}`}
                            onClick={handleStopClick}
                            disabled={isStopping}
                        >
                            <IcStop /> {isStopping ? "Stopping…" : "Stop batch"}
                        </button>
                    )}
                    {!isActive && !isArchived && (
                        <button className={styles.actionBtn} onClick={stop(onArchive)}>
                            <IcArchive /> Archive
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}

// ── Section header ────────────────────────────────────────────────────────────
function SectionHead({ title, hint, count }: { title: string; hint?: string; count: number }) {
    return (
        <div className={styles.sectionHead}>
            <h3 className={styles.sectionTitle}>{title}</h3>
            <span className={styles.countPill}>{count}</span>
            {hint && <span className={styles.sectionHint}>{hint}</span>}
            <div className={styles.rule} />
        </div>
    );
}

// ── Page ──────────────────────────────────────────────────────────────────────
export default function BatchesPage() {
    const [batches, setBatches] = useState<Batch[]>([]);
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [tab, setTab] = useState<Tab>("batches");
    const [query, setQuery] = useState("");

    const [isStartModalOpen, setIsStartModalOpen] = useState(false);
    const [logBatchId, setLogBatchId] = useState<number | null>(null);
    const [detailBatchId, setDetailBatchId] = useState<number | null>(null);
    const [endpointBatchId, setEndpointBatchId] = useState<number | null>(null);
    const [promptBatchId, setPromptBatchId] = useState<number | null>(null);
    const [exportBatchId, setExportBatchId] = useState<number | null>(null);
    const [clonePrompt, setClonePrompt] = useState<Prompt | null>(null);
    const [expandedBatchId, setExpandedBatchId] = useState<number | null>(null);

    // ── Load all batches, prompts & endpoints ─────────────────────────────────
    useEffect(() => {
        BatchesAPI.getAll().then(setBatches);
        PromptsAPI.getAll().then(setPrompts);
        EndpointsAPI.getAll().then(setEndpoints);
    }, []);

    // ── Auto-refresh while any batch is active ────────────────────────────────
    useEffect(() => {
        const hasActive = batches.some(b => ACTIVE_STATUSES.includes(b.status));
        if (!hasActive) return;
        const id = setInterval(() => BatchesAPI.getAll().then(setBatches), 5000);
        return () => clearInterval(id);
    }, [batches]);

    // ── Derived counts & filtered lists ──────────────────────────────────────
    const counts = useMemo(() => ({
        batches:  batches.filter(b => !b.archived_at).length,
        archived: batches.filter(b =>  b.archived_at).length,
    }), [batches]);

    const filtered = useMemo(() => {
        const q = query.trim();
        const nonArchived = batches.filter(b => !b.archived_at);
        const archived    = batches.filter(b =>  b.archived_at);
        return {
            active:   sortActive(nonArchived.filter(b => ACTIVE_STATUSES.includes(b.status) && matchSearch(b, q))),
            history:  sortHistory(nonArchived.filter(b => !ACTIVE_STATUSES.includes(b.status) && matchSearch(b, q))),
            archived: archived.filter(b => matchSearch(b, q)),
        };
    }, [batches, query]);

    // ── Actions ───────────────────────────────────────────────────────────────
    function openDetail(batch: Batch) {
        setDetailBatchId(batch.id);
    }

    function handleStop(batch: Batch): Promise<void> {
        return BatchesAPI.stop(batch.id)
            .then(updated => setBatches(prev => prev.map(b => b.id === updated.id ? updated : b)))
            .catch(err => { alert(err); console.error(err); });
    }

    function handleArchive(batch: Batch) {
        BatchesAPI.archive(batch.id).then(updated =>
            setBatches(prev => prev.map(b => b.id === updated.id ? updated : b))
        ).catch(err => { alert(err); console.error(err); });
    }

    function handleExport(batch: Batch) {
        setExportBatchId(batch.id);
    }

    const cardHandlers = {
        onToggleExpanded: (b: Batch) => setExpandedBatchId(prev => prev === b.id ? null : b.id),
        onDetails:  openDetail,
        onLog:      (b: Batch) => setLogBatchId(b.id),
        onExport:   handleExport,
        onStop:     handleStop,
        onArchive:  handleArchive,
        onEndpoint: (b: Batch) => setEndpointBatchId(b.id),
        onPrompt:   (b: Batch) => setPromptBatchId(b.id),
    };

    const logBatch    = batches.find(b => b.id === logBatchId)    ?? null;
    const detailBatch = batches.find(b => b.id === detailBatchId) ?? null;
    const exportBatch = batches.find(b => b.id === exportBatchId) ?? null;

    const promptForBatch = batches.find(b => b.id === promptBatchId) ?? null;
    const viewedPrompt   = promptForBatch ? prompts.find(p => p.id === promptForBatch.prompt_id) ?? null : null;

    const endpointForBatch = batches.find(b => b.id === endpointBatchId) ?? null;
    const viewedEndpoint   = endpointForBatch ? endpoints.find(e => e.id === endpointForBatch.endpoint_id) ?? null : null;

    function handleEditClonePrompt(prompt: Prompt) {
        setPromptBatchId(null);
        setClonePrompt(prompt);
    }

    const totallyEmpty = filtered.active.length === 0 && filtered.history.length === 0;

    const nonArchivedCount = counts.batches;

    return (
        <section className={styles.page}>

            {/* ── Page header ──────────────────────────────────────── */}
            <PageHeader
                title="Batch Runs"
                subtitle="All your batches — running, queued, and finished."
                count={nonArchivedCount}
                addLabel="Start Batch"
                onAdd={() => setIsStartModalOpen(true)}
            />

            {/* ── Toolbar ──────────────────────────────────────────── */}
            <div className={styles.toolbar}>
                <div className={styles.tabs} role="tablist">
                    {(["batches", "archived"] as Tab[]).map(t => (
                        <button
                            key={t}
                            role="tab"
                            aria-selected={tab === t}
                            className={`${styles.tab}${tab === t ? ` ${styles.tabActive}` : ""}`}
                            onClick={() => setTab(t)}
                        >
                            {t.charAt(0).toUpperCase() + t.slice(1)}
                            <span className={styles.tabCount}>{counts[t]}</span>
                        </button>
                    ))}
                </div>

                <div className={styles.search}>
                    <IcSearch />
                    <input
                        type="search"
                        placeholder="Search by name, model, endpoint, id…"
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                    />
                </div>

            </div>

            {/* ── Tab: Batches ─────────────────────────────────────── */}
            {tab === "batches" && (
                <>
                    {totallyEmpty && !query && (
                        <div className={styles.emptyState}>No batches yet. Click &ldquo;Start Batch&rdquo; to begin.</div>
                    )}
                    {totallyEmpty && query && (
                        <div className={styles.emptyState}>No batches match your search.</div>
                    )}

                    {!totallyEmpty && (
                        <>
                            <SectionHead title="Active" hint="Running and queued" count={filtered.active.length} />
                            <div className={styles.list}>
                                {filtered.active.length === 0
                                    ? <div className={styles.emptyState}>No batches are currently running or queued.</div>
                                    : filtered.active.map(b => <BatchCard key={b.id} batch={b} isExpanded={expandedBatchId === b.id} {...cardHandlers} />)
                                }
                            </div>

                            <SectionHead title="History" hint="Finished and stopped" count={filtered.history.length} />
                            <div className={styles.list}>
                                {filtered.history.length === 0
                                    ? <div className={styles.emptyState}>{query ? "No finished batches match your search." : "No finished batches yet."}</div>
                                    : filtered.history.map(b => <BatchCard key={b.id} batch={b} isExpanded={expandedBatchId === b.id} {...cardHandlers} />)
                                }
                            </div>
                        </>
                    )}
                </>
            )}

            {/* ── Tab: Archived ────────────────────────────────────── */}
            {tab === "archived" && (
                <>
                    <SectionHead title="Archived" count={filtered.archived.length} />
                    <div className={styles.list}>
                        {filtered.archived.length === 0
                            ? <div className={styles.emptyState}>{query ? "No archived batches match your search." : "No archived batches."}</div>
                            : filtered.archived.map(b => <BatchCard key={b.id} batch={b} isExpanded={expandedBatchId === b.id} {...cardHandlers} />)
                        }
                    </div>
                </>
            )}

            {/* ── Modals ───────────────────────────────────────────── */}
            <StartBatchModal
                isOpen={isStartModalOpen}
                onClose={() => setIsStartModalOpen(false)}
                onCreated={(newBatch: Batch) => {
                    setBatches(prev => [...prev, newBatch]);
                    // The create response is missing backend-computed fields
                    // (e.g. progress), so refetch right away to replace it.
                    BatchesAPI.getAll().then(setBatches);
                }}
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
                    key={detailBatch.id}
                    isOpen={!!detailBatchId}
                    onClose={() => setDetailBatchId(null)}
                    batch={detailBatch}
                    onViewEndpoint={() => { setEndpointBatchId(detailBatch.id); setDetailBatchId(null); }}
                    onViewPrompt={() => { setPromptBatchId(detailBatch.id); setDetailBatchId(null); }}
                />
            )}

            <EndpointModal
                endpoint={viewedEndpoint}
                onClose={() => setEndpointBatchId(null)}
                onUpdated={(updated) =>
                    setEndpoints(prev => prev.map(ep => ep.id === updated.id ? updated : ep))
                }
            />

            <PromptModal
                prompt={viewedPrompt}
                onClose={() => setPromptBatchId(null)}
                onEditClone={handleEditClonePrompt}
            />

            <AddPromptModal
                isOpen={!!clonePrompt}
                onClose={() => setClonePrompt(null)}
                onCreated={(newPrompt) => setPrompts(prev => [...prev, newPrompt])}
                initial={clonePrompt ? {
                    name: `${clonePrompt.name}_copy`,
                    content: clonePrompt.content,
                    multi_prompt: clonePrompt.multi_prompt,
                } : undefined}
            />

            {exportBatch && (
                <ExportModal
                    isOpen={!!exportBatchId}
                    onClose={() => setExportBatchId(null)}
                    batch={exportBatch}
                />
            )}
        </section>
    );
}

// ── Icons ─────────────────────────────────────────────────────────────────────
function IcSearch() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" width="14" height="14">
            <circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" />
        </svg>
    );
}
function IcDetails() {
    return (
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="2" width="12" height="12" rx="2" /><line x1="5" y1="8" x2="11" y2="8" /><line x1="8" y1="5" x2="8" y2="11" />
        </svg>
    );
}
function IcLog() {
    return (
        <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <line x1="2" y1="4" x2="14" y2="4" /><line x1="2" y1="8" x2="14" y2="8" /><line x1="2" y1="12" x2="10" y2="12" />
        </svg>
    );
}
function IcStop() {
    return (
        <svg viewBox="0 0 16 16" fill="currentColor"><rect x="3" y="3" width="10" height="10" rx="1.5" /></svg>
    );
}
function IcArchive() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2.5" y="4" width="19" height="4.5" rx="1" />
            <path d="M4 8.5V19a1.5 1.5 0 0 0 1.5 1.5h13A1.5 1.5 0 0 0 20 19V8.5" />
            <line x1="10" y1="13" x2="14" y2="13" />
        </svg>
    );
}
function IcChevron({ className }: { className?: string }) {
    return (
        <svg className={className} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" width="12" height="12">
            <polyline points="4 6 8 10 12 6" />
        </svg>
    );
}
function IcExport() {
    return (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 3v13" /><polyline points="7 11 12 16 17 11" /><path d="M5 20h14" />
        </svg>
    );
}
