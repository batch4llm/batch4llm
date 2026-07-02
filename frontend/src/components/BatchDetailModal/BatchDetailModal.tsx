import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { BatchesAPI } from "../../api/batches.ts";
import { type Batch, ACTIVE_STATUSES } from "../../types/Batch.ts";
import type { BatchFileOverview, BatchFileDetail } from "../../types/BatchFile.ts";
import type { BatchTaskDetail, BatchTaskPreview, LlmAttempt, BatchTaskStatus } from "../../types/BatchTask.ts";
import styles from "./BatchDetailModal.module.css";

interface Props {
    isOpen: boolean;
    onClose: () => void;
    batch: Batch;
}

// ── Formatting helpers ─────────────────────────────────────────────────────
function pillStyle(status: string): React.CSSProperties {
    const base: React.CSSProperties = {
        display: "inline-block",
        padding: "2px 7px",
        borderRadius: "999px",
        fontSize: "10.5px",
        flexShrink: 0,
    };
    if (status === "COMPLETED") {
        return { ...base, fontWeight: 500, background: "#f0fdf4", border: "1px solid #bbf7d0", color: "#15803d" };
    }
    const bg: Record<string, string> = { FAILED: "#e53935", RUNNING: "#1e88e5", QUEUED: "#9e9e9e" };
    return { ...base, fontWeight: 600, background: bg[status] ?? "#9e9e9e", color: "white" };
}

function statusLabel(status: string): string {
    return status === "COMPLETED" ? "done" : status.toLowerCase();
}

function fmtCost(v?: number | null): string {
    return v != null && v > 0 ? `$${v.toFixed(4)}` : "—";
}

function fmtDuration(start?: string, stop?: string): string {
    if (!start) return "—";
    const end = stop ? new Date(stop).getTime() : Date.now();
    const ms = end - new Date(start).getTime();
    if (ms < 0) return "—";
    if (ms < 1000) return `${ms} ms`;
    const secs = Math.floor(ms / 1000);
    if (secs < 60) return `${(ms / 1000).toFixed(1)} s`;
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

function fmtDateTime(v?: string): string {
    if (!v) return "—";
    return new Date(v).toLocaleString();
}

function jsonPretty(content: string): string {
    try {
        const parsed = JSON.parse(content);
        return typeof parsed === "string" ? parsed : JSON.stringify(parsed, null, 2);
    } catch {
        return content;
    }
}

function truncate(str: string | undefined | null, n: number): string {
    if (!str) return "";
    return str.length > n ? `${str.slice(0, n)}…` : str;
}

// ── Component ──────────────────────────────────────────────────────────────
export function BatchDetailModal({ isOpen, onClose, batch }: Props) {
    const [files, setFiles] = useState<BatchFileOverview[]>([]);
    const [selectedFileId, setSelectedFileId] = useState<number | null>(null);
    const [fileDetail, setFileDetail] = useState<BatchFileDetail | null>(null);
    const [selectedTaskId, setSelectedTaskId] = useState<number | null>(null);
    const [taskDetail, setTaskDetail] = useState<BatchTaskDetail | null>(null);
    const [paramsExpanded, setParamsExpanded] = useState(false);

    const isActive = ACTIVE_STATUSES.includes(batch.status);

    // Load file overview (and refresh while the batch is active).
    useEffect(() => {
        if (!isOpen) return;
        let cancelled = false;
        const load = () =>
            BatchesAPI.getBatchFiles(batch.id).then(fs => {
                if (cancelled) return;
                setFiles(fs);
                setSelectedFileId(prev => prev ?? fs[0]?.id ?? null);
            });
        load();
        if (!isActive) return () => { cancelled = true; };
        const id = setInterval(load, 5000);
        return () => { cancelled = true; clearInterval(id); };
    }, [isOpen, batch.id, isActive]);

    // Load the selected file's tasks (and refresh while active).
    useEffect(() => {
        if (!isOpen || selectedFileId == null) return;
        let cancelled = false;
        const load = () =>
            BatchesAPI.getBatchFile(selectedFileId).then(fd => {
                if (cancelled) return;
                setFileDetail(fd);
                setSelectedTaskId(prev =>
                    prev != null && fd.batch_tasks.some(t => t.id === prev)
                        ? prev
                        : fd.batch_tasks[0]?.id ?? null
                );
            });
        load();
        if (!isActive) return () => { cancelled = true; };
        const id = setInterval(load, 5000);
        return () => { cancelled = true; clearInterval(id); };
    }, [isOpen, selectedFileId, isActive]);

    // Load the selected task's detail (and refresh while active).
    useEffect(() => {
        if (!isOpen || selectedTaskId == null) return;
        let cancelled = false;
        const load = () =>
            BatchesAPI.getBatchTask(selectedTaskId).then(td => {
                if (!cancelled) setTaskDetail(td);
            });
        load();
        if (!isActive) return () => { cancelled = true; };
        const id = setInterval(load, 5000);
        return () => { cancelled = true; clearInterval(id); };
    }, [isOpen, selectedTaskId, isActive]);

    if (!isOpen) return null;

    // ── Derived header values ──
    const completedFiles = files.filter(f => f.status === "COMPLETED").length;
    const totalTasks = files.reduce((s, f) => s + f.task_count, 0);
    const doneTasks = files.reduce((s, f) => s + f.completed_task_count, 0);

    const stepLabel = (t: { prompt_marker?: string }): string =>
        t.prompt_marker && t.prompt_marker !== "-" ? t.prompt_marker : "Task";

    const taskPreviewClass = (status: BatchTaskStatus) =>
        status === "FAILED" ? styles.taskPreviewFailed
            : status === "QUEUED" ? styles.taskPreviewQueued
            : "";

    function previewText(t: BatchTaskPreview): string {
        if (t.output_preview) return truncate(t.output_preview, 140);
        if (t.status === "QUEUED") return "Waiting for previous step to complete.";
        if (t.status === "RUNNING") return "Running…";
        if (t.status === "FAILED") return "Failed — see task detail.";
        return "—";
    }

    const params: { label: string; value: string }[] = [
        { label: "file reader", value: batch.file_reader ?? "—" },
        { label: "temperature", value: batch.temperature != null ? String(batch.temperature) : "—" },
        { label: "json format", value: batch.json_format ? "on" : "off" },
    ];

    const content = (
        <div className={styles.backdrop} onMouseDown={onClose}>
            <div className={styles.shell} onMouseDown={e => e.stopPropagation()}>

                {/* ── Header ─────────────────────────────────────────── */}
                <div className={styles.header}>
                    <div className={styles.headerTop}>
                        <button className={styles.breadcrumb} onClick={onClose}>
                            <svg width="10" height="10" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round"><path d="M10 12L6 8l4-4" /></svg>
                            Batch Runs
                        </button>
                        <div className={styles.titleRow}>
                            <div className={styles.titleLeft}>
                                <h1 className={styles.title}>Batch #{batch.id}</h1>
                                <span style={pillStyle(batch.status)}>{statusLabel(batch.status)}</span>
                                <span className={styles.chip}>
                                    <span className={styles.chipKey}>Model</span>
                                    <span className={styles.chipVal}>{batch.model}</span>
                                </span>
                                <span className={styles.chip}>
                                    <span className={styles.chipKey}>Endpoint</span>
                                    <span className={styles.chipVal}>{batch.endpoint_name ?? `#${batch.endpoint_id}`}</span>
                                </span>
                                <span className={styles.chip}>
                                    <span className={styles.chipKey}>Prompt</span>
                                    <span className={styles.chipVal}>{batch.prompt_name ?? `#${batch.prompt_id}`}</span>
                                </span>
                            </div>
                            <div className={styles.stats}>
                                <div>
                                    <div className={styles.statKey}>Files</div>
                                    <div className={styles.statVal}>{completedFiles} / {files.length}</div>
                                </div>
                                <div className={styles.statDivider} />
                                <div>
                                    <div className={styles.statKey}>Tasks</div>
                                    <div className={styles.statVal}>{doneTasks} / {totalTasks}</div>
                                </div>
                                <div className={styles.statDivider} />
                                <div>
                                    <div className={styles.statKey}>Cost</div>
                                    <div className={styles.statVal}>{fmtCost(batch.costs_in_usd)}</div>
                                </div>
                                <div className={styles.statDivider} />
                                <div>
                                    <div className={styles.statKey}>Duration</div>
                                    <div className={styles.statVal}>{fmtDuration(batch.started_at, batch.stopped_at)}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Parameters strip */}
                    <div className={styles.params}>
                        <button className={styles.paramsToggle} onClick={() => setParamsExpanded(v => !v)}>
                            Parameters {paramsExpanded ? "▾" : "▸"}
                        </button>
                        {paramsExpanded && (
                            <div className={styles.paramList}>
                                {params.map(p => (
                                    <span key={p.label} className={styles.chip}>
                                        <span className={styles.chipKey}>{p.label}</span>
                                        <span className={styles.chipVal}>{p.value}</span>
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* ── Three panels ───────────────────────────────────── */}
                <div className={styles.panels}>

                    {/* Panel 1: Files */}
                    <div className={`${styles.panel} ${styles.panelFiles}`}>
                        <div className={styles.panelHead}>
                            <span className={styles.panelHeadLabel}>Files</span>
                            <span className={styles.panelHeadCount}>{files.length}</span>
                        </div>
                        <div className={styles.panelBody}>
                            {files.map(file => {
                                const failed = file.task_count - file.completed_task_count;
                                const meta = file.status === "FAILED" || failed > 0
                                    ? `${file.completed_task_count}/${file.task_count} done`
                                    : `${file.completed_task_count}/${file.task_count} tasks`;
                                return (
                                    <div
                                        key={file.id}
                                        className={`${styles.fileRow}${file.id === selectedFileId ? ` ${styles.selected}` : ""}`}
                                        onClick={() => { setSelectedFileId(file.id); setSelectedTaskId(null); }}
                                    >
                                        <div className={styles.fileTop}>
                                            <span className={styles.fileName}>{file.name}</span>
                                            <span style={pillStyle(file.status)}>{statusLabel(file.status)}</span>
                                        </div>
                                        <div className={styles.fileMeta}>
                                            <span className={styles.metaMuted}>{meta}</span>
                                        </div>
                                    </div>
                                );
                            })}
                            {files.length === 0 && <div className={styles.empty}>No files in this batch.</div>}
                        </div>
                    </div>

                    {/* Panel 2: Tasks */}
                    <div className={`${styles.panel} ${styles.panelTasks}`}>
                        <div className={styles.panelHead}>
                            <span className={styles.panelHeadLabel}>Tasks</span>
                            {fileDetail && <span className={styles.panelHeadCount}>{fmtCost(fileDetail.costs_in_usd)}</span>}
                        </div>
                        <div className={styles.panelBody}>
                            {selectedFileId == null && <div className={styles.empty}>Select a file to view its tasks.</div>}
                            {selectedFileId != null && fileDetail?.batch_tasks.map(task => (
                                <div
                                    key={task.id}
                                    className={`${styles.taskRow}${task.id === selectedTaskId ? ` ${styles.selected}` : ""}`}
                                    onClick={() => setSelectedTaskId(task.id)}
                                >
                                    <div className={styles.taskTop}>
                                        <div className={styles.taskTitle}>
                                            <span className={styles.stepLabel}>{stepLabel(task)}</span>
                                            {task.retry_count > 0 && (
                                                <span className={styles.metaMuted}>· {task.retry_count} retr{task.retry_count === 1 ? "y" : "ies"}</span>
                                            )}
                                        </div>
                                        <span style={pillStyle(task.status)}>{statusLabel(task.status)}</span>
                                    </div>
                                    <div className={`${styles.taskPreview} ${taskPreviewClass(task.status)}`}>
                                        {previewText(task)}
                                    </div>
                                    <div className={styles.taskCost}>{fmtCost(task.costs_in_usd)}</div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Panel 3: Task detail */}
                    <div className={`${styles.panel} ${styles.panelDetail}`}>
                        <div className={`${styles.panelHead} ${styles.panelHeadDetail}`}>
                            <span className={styles.panelHeadLabel}>Task Detail</span>
                        </div>
                        <div className={styles.detailBody}>
                            {selectedTaskId != null && taskDetail?.id === selectedTaskId ? (
                                <TaskDetailView key={taskDetail.id} task={taskDetail} fileName={fileDetail?.name ?? ""} />
                            ) : (
                                <div className={styles.emptyCenter}>
                                    Select a task to view its output and attempts.
                                </div>
                            )}
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );

    return createPortal(content, document.body);
}

// ── Collapsible prompt card (System / User) ────────────────────────────────
const PROMPT_PREVIEW_LENGTH = 300;

function PromptCard({ kind, text }: { kind: "system" | "user"; text: string }) {
    const truncated = text.length > PROMPT_PREVIEW_LENGTH;
    const [expanded, setExpanded] = useState(false);
    const preview = truncated ? `${text.slice(0, PROMPT_PREVIEW_LENGTH)}…` : text;

    return (
        <div className={styles.promptCard}>
            <div className={styles.promptHeader} onClick={() => truncated && setExpanded(v => !v)}>
                <span className={`${styles.promptBadge} ${kind === "system" ? styles.promptBadgeSystem : styles.promptBadgeUser}`}>
                    {kind}
                </span>
                <span className={styles.promptPreview}>{preview}</span>
                {truncated && <span className={styles.promptChevron}>{expanded ? "▾" : "▸"}</span>}
            </div>
            {expanded && <pre className={styles.promptBody}>{text}</pre>}
        </div>
    );
}

// ── Task detail panel ──────────────────────────────────────────────────────
// The API ships the raw attempts; the result, cost, tokens, retry count and
// failed list are all derived here rather than on the server.
function TaskDetailView({ task, fileName }: { task: BatchTaskDetail; fileName: string }) {
    const marker = task.prompt_marker && task.prompt_marker !== "-" ? task.prompt_marker : "Task";

    const attempts = [...task.attempts].sort(
        (a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
    );
    const winner = attempts.find(a => a.status === "COMPLETED") ?? null;
    const failed = attempts.filter(a => a.status === "FAILED");
    const totalCost = attempts.reduce((s, a) => s + (a.costs_in_usd ?? 0), 0);
    const attemptNumber = (att: LlmAttempt) => attempts.indexOf(att) + 1;

    const hasSystem = !!task.system_prompt;
    const hasUser = !!task.user_input;

    return (
        <>
            {/* Summary card */}
            <div className={styles.summaryCard}>
                <div className={styles.summaryTop}>
                    <div className={styles.summaryTitle}>
                        <span className={styles.stepLabel}>{marker}</span>
                        <span className={styles.summaryName}>#{task.id}</span>
                    </div>
                    <span style={pillStyle(task.status)}>{statusLabel(task.status)}</span>
                </div>
                <div className={styles.summaryGrid}>
                    <div>
                        <div className={styles.fieldKey}>File</div>
                        <div className={styles.fieldVal}>{fileName || "—"}</div>
                    </div>
                    <div>
                        <div className={styles.fieldKey}>Duration</div>
                        <div className={styles.fieldVal}>{fmtDuration(task.started_at, task.stopped_at)}</div>
                    </div>
                    <div>
                        <div className={styles.fieldKey}>Cost</div>
                        <div className={styles.fieldVal}>{fmtCost(totalCost)}</div>
                    </div>
                    <div>
                        <div className={styles.fieldKey}>Tokens</div>
                        <div className={styles.fieldVal}>
                            ↑ {winner?.input_token_count ?? "—"} · ↓ {winner?.output_token_count ?? "—"}
                        </div>
                    </div>
                    <div>
                        <div className={styles.fieldKey}>Attempts</div>
                        <div className={styles.fieldVal}>{attempts.length || 1}</div>
                    </div>
                </div>
            </div>

            {/* Prompts — shown once, shared across all attempts */}
            {(hasSystem || hasUser) && (
                <div className={styles.section}>
                    <div className={styles.sectionLabel}>Prompts</div>
                    {hasSystem && <PromptCard kind="system" text={task.system_prompt!} />}
                    {hasUser && <PromptCard kind="user" text={task.user_input!} />}
                </div>
            )}

            {/* Result — always shown on top when one succeeded */}
            {winner?.output != null && (
                <div className={styles.section}>
                    <div className={styles.sectionLabel}>Result</div>
                    <div className={`${styles.attemptCard} ${styles.attemptCardResult}`}>
                        <div className={styles.attemptHeader}>
                            <div className={styles.attemptHeaderLeft}>
                                <span className={styles.attemptLabel}>Success</span>
                            </div>
                            <div className={styles.attemptMeta}>
                                <span className={styles.attemptMetaMono}>
                                    ↑ {winner.input_token_count ?? "—"} ↓ {winner.output_token_count ?? "—"} tok
                                </span>
                                <span style={pillStyle("COMPLETED")}>done</span>
                            </div>
                        </div>
                        <div className={styles.attemptBody}>
                            <pre className={styles.responseBox}>{jsonPretty(winner.output)}</pre>
                        </div>
                    </div>
                </div>
            )}

            {/* Failed attempts — listed below the result, with their reason */}
            {failed.length > 0 && (
                <div className={styles.section}>
                    <div className={styles.sectionLabel}>
                        Failed attempts · {failed.length}
                    </div>
                    {failed.map(att => (
                        <div key={att.id} className={styles.attemptCard}>
                            <div className={styles.attemptHeader}>
                                <div className={styles.attemptHeaderLeft}>
                                    <span className={styles.attemptLabel}>Attempt {attemptNumber(att)}</span>
                                    <span className={styles.attemptMetaMono}>{fmtDateTime(att.created_at)}</span>
                                </div>
                                <div className={styles.attemptMeta}>
                                    <span className={styles.attemptMetaMono}>{fmtCost(att.costs_in_usd)}</span>
                                    <span style={pillStyle("FAILED")}>failed</span>
                                </div>
                            </div>
                            <div className={styles.attemptBody}>
                                <div className={styles.errorBox}>
                                    {att.reason ?? "No failure reason recorded yet."}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Nothing to show yet */}
            {winner?.output == null && failed.length === 0 && (
                <div className={styles.emptyCenter}>
                    {task.status === "QUEUED" || task.status === "RUNNING"
                        ? "No output yet — this task is still in progress."
                        : "No output available for this task."}
                </div>
            )}
        </>
    );
}
