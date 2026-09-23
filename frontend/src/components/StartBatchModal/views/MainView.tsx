import { useEffect, useRef } from "react";
import type { ModelInfo } from "../../../types/Model";
import { logoFor } from "../../../utils/providerLogo";
import { fmtCost } from "../formatCost.ts";
import { displayModelName } from "../formatModelName.ts";
import styles from "../StartBatchModal.module.css";
import { SelectorRow } from "../components/SelectorRow.tsx";
import { Collapsible } from "../components/Collapsible.tsx";
import { ApiParamRow } from "../components/ApiParamRow.tsx";
import type { ApiParams, FileMode, InvalidField } from "../types.ts";
import { IconModel, IconFiles, IconPrompt, IconFileHandling, IconPlay, IconSample, IconCheck } from "../Icons.tsx";

type Props = {
    // Reset
    onResetAll: () => void;

    // Name
    batchName: string;
    onSetBatchName: (v: string) => void;
    batchNamePlaceholder: string;

    // Model
    selectedModel: ModelInfo | null;
    onOpenModel: () => void;

    // Files
    filesValue?: string;
    filesSub?: string;
    onOpenFiles: () => void;

    // Prompt
    promptValue?: string;
    promptSub?: string;
    onOpenPrompt: () => void;

    // File handling
    fileMode: FileMode;
    onSetFileMode: (mode: FileMode) => void;
    fileReaderValue?: string;
    fileReaderSub?: string;
    onOpenFileReader: () => void;

    // Validation
    invalid: Partial<Record<InvalidField, boolean>>;

    // Model settings
    modelSettingsOpen: boolean;
    onToggleModelSettings: () => void;
    jsonFormat: boolean;
    onSetJsonFormat: (v: boolean) => void;
    temperature: number;
    onSetTemperature: (v: number) => void;
    apiParams: ApiParams;
    onActivateParam: (key: keyof ApiParams, value: number) => void;
    onResetParam: (key: keyof ApiParams) => void;

    // Batch settings
    batchSettingsOpen: boolean;
    onToggleBatchSettings: () => void;
    adaptiveRateLimiting: boolean;
    onSetAdaptiveRateLimiting: (v: boolean) => void;
    maxTasksPerMinute: number;
    onSetMaxTasksPerMinute: (v: number) => void;
    allowConcurrency: boolean;
    onSetAllowConcurrency: (v: boolean) => void;
    retriesPerFailedTask: number;
    onSetRetriesPerFailedTask: (v: number) => void;
    failureThresholdPercent: number;
    onSetFailureThresholdPercent: (v: number) => void;

    // Estimate
    estimateOpen: boolean;
    onToggleEstimate: () => void;
    onRunEstimate: () => void;
    sampleOutputSet: boolean;
    onOpenSampleOutput: () => void;

    // Actions
    scheduleActive: boolean;
    onToggleSchedule: () => void;
    providerActive: boolean;
    onToggleProviderBatch: () => void;
    scheduledAt: string;
    onSetScheduledAt: (v: string) => void;
    onStart: () => void;
    submitting: boolean;
};

export function MainView({
    onResetAll,
    batchName, onSetBatchName, batchNamePlaceholder,
    selectedModel, onOpenModel,
    filesValue, filesSub, onOpenFiles,
    promptValue, promptSub, onOpenPrompt,
    fileMode, onSetFileMode, fileReaderValue, fileReaderSub, onOpenFileReader,
    invalid,
    modelSettingsOpen, onToggleModelSettings, jsonFormat, onSetJsonFormat,
    temperature, onSetTemperature, apiParams, onActivateParam, onResetParam,
    batchSettingsOpen, onToggleBatchSettings,
    adaptiveRateLimiting, onSetAdaptiveRateLimiting,
    maxTasksPerMinute, onSetMaxTasksPerMinute,
    allowConcurrency, onSetAllowConcurrency,
    retriesPerFailedTask, onSetRetriesPerFailedTask,
    failureThresholdPercent, onSetFailureThresholdPercent,
    estimateOpen, onToggleEstimate, onRunEstimate, sampleOutputSet, onOpenSampleOutput,
    scheduleActive, onToggleSchedule, providerActive, onToggleProviderBatch,
    scheduledAt, onSetScheduledAt, onStart, submitting,
}: Props) {
    const scheduleBoxRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scheduleActive || providerActive) {
            scheduleBoxRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
        }
    }, [scheduleActive, providerActive]);

    return (
        <div className={styles.view}>
            <div className={styles.mainHeaderRow}>
                <div>
                    <h2 className={styles.mainTitle}>Start Batch</h2>
                    <p className={styles.mainSub}>Configure and launch a new file batch.</p>
                </div>
                <button type="button" className={styles.resetAllBtn} onClick={onResetAll}>
                    Reset all
                </button>
            </div>

            <div className={styles.nameField}>
                <label className={styles.nameFieldLabel}>Batch Name</label>
                <input
                    type="text"
                    className={styles.fieldInput}
                    value={batchName}
                    placeholder={batchNamePlaceholder}
                    maxLength={200}
                    onChange={(e) => onSetBatchName(e.target.value)}
                />
            </div>

            <div className={styles.selectorStack}>
                <SelectorRow
                    icon={selectedModel ? <img src={logoFor(selectedModel.provider)} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }} /> : <IconModel />}
                    label="Model"
                    value={selectedModel ? `${displayModelName(selectedModel.model_name)} · ${selectedModel.endpoint_name}` : undefined}
                    emptyText="Select a model..."
                    sub={selectedModel
                        ? `$${fmtCost(selectedModel.input_cost_per_1m_tokens)} / $${fmtCost(selectedModel.output_cost_per_1m_tokens)} per 1M tokens`
                        : undefined}
                    invalid={invalid.model}
                    onClick={onOpenModel}
                />
                <SelectorRow
                    icon={<IconFiles />}
                    label="Files"
                    value={filesValue}
                    emptyText="Select files or tags..."
                    sub={filesSub}
                    invalid={invalid.files}
                    onClick={onOpenFiles}
                />
                <SelectorRow
                    icon={<IconPrompt />}
                    label="Prompt"
                    value={promptValue}
                    emptyText="Select a prompt..."
                    sub={promptSub}
                    invalid={invalid.prompt}
                    onClick={onOpenPrompt}
                />
            </div>

            {/* File Handling row */}
            <div
                className={`${styles.selectorRow}${invalid.filereader ? ` ${styles.invalid}` : ""}`}
                style={{ cursor: "pointer", marginBottom: 16 }}
                onClick={() => fileMode === "reader" && onOpenFileReader()}
            >
                <div className={styles.selectorIcon}><IconFileHandling /></div>
                <div className={styles.selectorBody}>
                    <div className={styles.selectorLabel}>File Handling</div>
                    {fileMode === "upload" ? (
                        <>
                            <div className={styles.selectorValue}>Direct Upload</div>
                            <div className={styles.selectorSub}>Provider receives file directly</div>
                        </>
                    ) : (
                        <>
                            {fileReaderValue
                                ? <div className={styles.selectorValue}>{fileReaderValue}</div>
                                : <div className={styles.selectorEmpty}>Select a reader...</div>}
                            {fileReaderSub && <div className={styles.selectorSub}>{fileReaderSub}</div>}
                        </>
                    )}
                </div>
                <div className={styles.segmented} onClick={(e) => e.stopPropagation()}>
                    <button
                        type="button"
                        className={`${styles.segmentedTab}${fileMode === "upload" ? ` ${styles.active}` : ""}`}
                        onClick={() => onSetFileMode("upload")}
                    >
                        Upload
                    </button>
                    <button
                        type="button"
                        className={`${styles.segmentedTab}${fileMode === "reader" ? ` ${styles.active}` : ""}`}
                        onClick={() => onSetFileMode("reader")}
                    >
                        File Reader
                    </button>
                </div>
            </div>

            <div className={styles.divider} />

            {/* Model Settings */}
            <Collapsible title="Model Settings" open={modelSettingsOpen} onToggle={onToggleModelSettings}>
                <div className={styles.fieldRow} style={{ marginBottom: 14 }}>
                    <label className={styles.fieldLabelLeft}>Answer Format</label>
                    <select
                        className={`${styles.fieldInput} ${styles.fieldInputMd}`}
                        value={jsonFormat ? "json" : "text"}
                        onChange={(e) => onSetJsonFormat(e.target.value === "json")}
                    >
                        <option value="text">Text</option>
                        <option value="json">JSON</option>
                    </select>
                </div>

                <div className={styles.thinDivider} />
                <div className={styles.sectionSublabel}>API Parameters</div>

                <ApiParamRow
                    paramKey="temperature" label="temperature"
                    tooltip="Controls randomness. Lower = more deterministic, higher = more creative."
                    kind="slider" min={0} max={3} step={0.1}
                    value={temperature} active alwaysActive
                    onChange={onSetTemperature}
                />
                <ApiParamRow
                    paramKey="top_p" label="top_p"
                    tooltip="Nucleus sampling threshold. Tokens with cumulative prob above top_p are excluded."
                    kind="slider" min={0} max={1} step={0.01}
                    value={apiParams.top_p} active={apiParams.top_p !== undefined}
                    onChange={(v) => onActivateParam("top_p", v)}
                    onReset={() => onResetParam("top_p")}
                />
                <ApiParamRow
                    paramKey="frequency_penalty" label="frequency_penalty"
                    tooltip="Reduces repetition of tokens based on how often they've appeared so far."
                    kind="slider" min={-2} max={2} step={0.1}
                    value={apiParams.frequency_penalty} active={apiParams.frequency_penalty !== undefined}
                    onChange={(v) => onActivateParam("frequency_penalty", v)}
                    onReset={() => onResetParam("frequency_penalty")}
                />
                <ApiParamRow
                    paramKey="presence_penalty" label="presence_penalty"
                    tooltip="Penalises tokens that have appeared at all, encouraging new topics."
                    kind="slider" min={-2} max={2} step={0.1}
                    value={apiParams.presence_penalty} active={apiParams.presence_penalty !== undefined}
                    onChange={(v) => onActivateParam("presence_penalty", v)}
                    onReset={() => onResetParam("presence_penalty")}
                />
                <ApiParamRow
                    paramKey="max_tokens" label="max_tokens"
                    tooltip="Maximum number of tokens the model may generate in a single response."
                    kind="number" min={1} max={8000} placeholder="e.g. 2048"
                    value={apiParams.max_tokens} active={apiParams.max_tokens !== undefined}
                    onChange={(v) => onActivateParam("max_tokens", v)}
                    onReset={() => onResetParam("max_tokens")}
                />
                <ApiParamRow
                    paramKey="seed" label="seed"
                    tooltip="Fixed seed for deterministic outputs. Same seed + same prompt = same result (where supported)."
                    kind="number" placeholder="e.g. 42"
                    value={apiParams.seed} active={apiParams.seed !== undefined}
                    onChange={(v) => onActivateParam("seed", v)}
                    onReset={() => onResetParam("seed")}
                />
            </Collapsible>

            {/* Batch Settings */}
            <Collapsible title="Batch Settings" open={batchSettingsOpen} onToggle={onToggleBatchSettings}>
                <div className={styles.primarySwitchRow}>
                    <div className={styles.fieldLabelWrap}>
                        <span className={styles.primarySwitchLabel}>Adaptive Rate Limiting</span>
                        <button type="button" className={styles.mpInfo} title="Automatically slows down dispatch when rate-limit errors occur, then speeds back up as errors clear. Recommended for almost all batches.">?</button>
                    </div>
                    <button
                        type="button"
                        className={`${styles.switch}${adaptiveRateLimiting ? ` ${styles.active}` : ""}`}
                        onClick={() => onSetAdaptiveRateLimiting(!adaptiveRateLimiting)}
                    >
                        <span className={styles.switchThumb} />
                    </button>
                </div>

                <div className={styles.fieldRow}>
                    <div className={styles.fieldLabelWrap}>
                        <label className={styles.fieldLabel}>Tasks / min</label>
                        <button type="button" className={styles.mpInfo} title="Starting point for how many tasks are dispatched per minute. With Adaptive Rate Limiting on, this is only the starting rate - it is adjusted automatically from here.">?</button>
                    </div>
                    <input
                        type="number" className={`${styles.fieldInput} ${styles.fieldInputSm}`}
                        min={1} max={20} value={maxTasksPerMinute}
                        onChange={(e) => onSetMaxTasksPerMinute(parseInt(e.target.value) || 1)}
                    />
                </div>

                <div className={styles.switchRow}>
                    <div className={styles.fieldLabelWrap}>
                        <span className={styles.switchLabel}>Allow Concurrency</span>
                        <button type="button" className={styles.mpInfo} title="If enabled, multiple tasks may run at the same time. Disable to force one request at a time, for providers that don't tolerate concurrent requests.">?</button>
                    </div>
                    <button
                        type="button"
                        className={`${styles.switch}${allowConcurrency ? ` ${styles.active}` : ""}`}
                        onClick={() => onSetAllowConcurrency(!allowConcurrency)}
                    >
                        <span className={styles.switchThumb} />
                    </button>
                </div>

                <div className={styles.fieldRow}>
                    <div className={styles.fieldLabelWrap}>
                        <label className={styles.fieldLabel}>Retries / Failed Task</label>
                        <button type="button" className={styles.mpInfo} title="How many times a single failed task is retried before it is marked as permanently failed.">?</button>
                    </div>
                    <input
                        type="number" className={`${styles.fieldInput} ${styles.fieldInputSm}`}
                        min={0} max={20} value={retriesPerFailedTask}
                        onChange={(e) => onSetRetriesPerFailedTask(parseInt(e.target.value) || 0)}
                    />
                </div>

                <div className={styles.fieldRow} style={{ marginBottom: 6 }}>
                    <div className={styles.fieldLabelWrap}>
                        <label className={styles.fieldLabel}>Failure Threshold</label>
                        <button type="button" className={styles.mpInfo} title="If this share of tasks fail, the batch is automatically cancelled.">?</button>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <input
                            type="range" min={0} max={100} step={1} value={failureThresholdPercent}
                            style={{ flex: 1, accentColor: "#1e1e2f", cursor: "pointer" }}
                            onChange={(e) => onSetFailureThresholdPercent(parseInt(e.target.value))}
                        />
                        <span style={{ fontSize: 12, fontFamily: "ui-monospace, monospace", fontWeight: 600, color: "#1e1e2f", minWidth: 36, textAlign: "right" }}>
                            {failureThresholdPercent}%
                        </span>
                    </div>
                </div>
                <div style={{ fontSize: 11, color: "#aaa", paddingLeft: 2 }}>
                    At {failureThresholdPercent}%: batch cancels after {failureThresholdPercent} of 100 tasks fail.
                </div>
            </Collapsible>

            {/* Estimate */}
            <Collapsible title="Estimate" open={estimateOpen} onToggle={onToggleEstimate} style={{ marginBottom: 20 }}>
                <div className={styles.estActions}>
                    <button type="button" className={`${styles.estBtn} ${styles.primary}`} onClick={onRunEstimate}>
                        <IconPlay /> Validate &amp; Estimate
                    </button>
                    <button
                        type="button"
                        className={`${styles.estBtn}${sampleOutputSet ? ` ${styles.sampleSet}` : ""}`}
                        onClick={onOpenSampleOutput}
                    >
                        {sampleOutputSet ? <IconCheck size={10} color="currentColor" /> : <IconSample />}
                        {sampleOutputSet ? "Sample set" : "Sample Output"}
                    </button>
                </div>
                <div className={styles.estPlaceholder}>Select model, files &amp; prompt — then run estimate.</div>
            </Collapsible>

            {/* Actions */}
            <div className={styles.actions}>
                <button type="button" className={styles.btnPrimary} onClick={onStart} disabled={submitting}>
                    {submitting ? "Starting…" : "Start"}
                </button>
                <button
                    type="button"
                    className={`${styles.btnToggle}${scheduleActive ? ` ${styles.active}` : ""}`}
                    onClick={onToggleSchedule}
                >
                    <span className={styles.toggleCheck}><IconCheck size={8} color="currentColor" /></span>
                    Schedule
                </button>
                <button
                    type="button"
                    className={`${styles.btnToggle}${providerActive ? ` ${styles.active}` : ""}`}
                    onClick={onToggleProviderBatch}
                >
                    <span className={styles.toggleCheck}><IconCheck size={8} color="currentColor" /></span>
                    Provider Batch
                </button>
            </div>

            {scheduleActive && (
                <div ref={scheduleBoxRef} className={`${styles.scheduleBox}${invalid.schedule ? ` ${styles.invalid}` : ""}`}>
                    <div className={styles.scheduleLabel}>Schedule for</div>
                    <input
                        type="datetime-local"
                        className={styles.fieldInput}
                        style={{ width: "100%" }}
                        value={scheduledAt}
                        onChange={(e) => onSetScheduledAt(e.target.value)}
                    />
                </div>
            )}

            {providerActive && (
                <div ref={scheduleBoxRef} className={styles.scheduleBox}>
                    <div className={styles.scheduleLabel}>Provider Batch</div>
                    <p className={styles.scheduleInfo}>
                        The batch is submitted as a single provider-side batch job (e.g. OpenAI Batch API). Lower cost, but results arrive asynchronously — usually within 24 hours.
                    </p>
                </div>
            )}
        </div>
    );
}
