import { useEffect, useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { BatchesAPI } from "../../api/batches.ts";
import { ModelsAPI } from "../../api/models.ts";
import { FilesAPI } from "../../api/files.ts";
import { PipelineAPI } from "../../api/pipeline.ts";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import type { Batch, BatchStartRequest } from "../../types/Batch.ts";
import type { ModelInfo } from "../../types/Model.ts";
import type { FileData } from "../../types/FileData.ts";
import type { ApiParams, FileMode, InvalidField, ViewId } from "./types.ts";
import { MainView } from "./views/MainView.tsx";
import { ModelView } from "./views/ModelView.tsx";
import { FilesView } from "./views/FilesView.tsx";
import { FileReaderView } from "./views/FileReaderView.tsx";
import { SampleOutputView } from "./views/SampleOutputView.tsx";
import { PromptView } from "./views/PromptView.tsx";
import styles from "./StartBatchModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (batch: Batch) => void;
};

function prettifyReaderId(id: string): string {
    return id.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
}

export function StartBatchModal({ isOpen, onClose, onCreated }: Props) {
    const [view, setView] = useState<ViewId>("main");

    // ── Data ─────────────────────────────────────────────────────────────
    const [models, setModels] = useState<ModelInfo[]>([]);
    const [loadingModels, setLoadingModels] = useState(false);
    const [files, setFiles] = useState<FileData[]>([]);
    const [loadingFiles, setLoadingFiles] = useState(false);
    const [fileTags, setFileTags] = useState<string[]>([]);
    const [loadingFileTags, setLoadingFileTags] = useState(false);
    const [fileReaders, setFileReaders] = useState<string[]>([]);
    const [loadingFileReaders, setLoadingFileReaders] = useState(false);
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [loadingPrompts, setLoadingPrompts] = useState(false);

    // ── Selections ───────────────────────────────────────────────────────
    const [selectedModel, setSelectedModel] = useState<ModelInfo | null>(null);
    const [selectedFileTags, setSelectedFileTags] = useState<string[]>([]);
    const [selectedFileIds, setSelectedFileIds] = useState<number[]>([]);
    const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
    const [fileMode, setFileMode] = useState<FileMode>("upload");
    const [selectedFileReader, setSelectedFileReader] = useState<string | null>(null);

    // ── Search ───────────────────────────────────────────────────────────
    const [modelSearch, setModelSearch] = useState("");
    const [fileSearch, setFileSearch] = useState("");

    // ── Collapsibles ─────────────────────────────────────────────────────
    const [modelSettingsOpen, setModelSettingsOpen] = useState(false);
    const [batchSettingsOpen, setBatchSettingsOpen] = useState(false);
    const [estimateOpen, setEstimateOpen] = useState(false);

    // ── Model settings ───────────────────────────────────────────────────
    const [temperature, setTemperature] = useState(1);
    const [jsonFormat, setJsonFormat] = useState(false);
    const [apiParams, setApiParams] = useState<ApiParams>({});

    // ── Batch settings ───────────────────────────────────────────────────
    const [maxTasksPerMinute, setMaxTasksPerMinute] = useState(5);
    const [maxParallelTasks, setMaxParallelTasks] = useState(1);
    const [retriesPerFailedTask, setRetriesPerFailedTask] = useState(2);
    const [failureThresholdPercent, setFailureThresholdPercent] = useState(20);
    const [queueBatch, setQueueBatch] = useState(true);
    const [intelligentBackoff, setIntelligentBackoff] = useState(true);

    // ── Sample output ────────────────────────────────────────────────────
    const [sampleOutputText, setSampleOutputText] = useState("");
    const [sampleOutputSet, setSampleOutputSet] = useState(false);

    // ── Schedule / Provider Batch ────────────────────────────────────────
    const [scheduleActive, setScheduleActive] = useState(false);
    const [providerActive, setProviderActive] = useState(false);
    const [scheduledAt, setScheduledAt] = useState("");

    // ── Validation / submit ──────────────────────────────────────────────
    const [invalid, setInvalid] = useState<Partial<Record<InvalidField, boolean>>>({});
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        if (!isOpen) return;

        const fetchData = async () => {
            setLoadingModels(true);
            setLoadingFiles(true);
            setLoadingFileTags(true);
            setLoadingFileReaders(true);
            setLoadingPrompts(true);

            try {
                const [mdls, fls, fTags, fReaders, prms] = await Promise.all([
                    ModelsAPI.getAll(),
                    FilesAPI.getAll(),
                    FilesAPI.getFileTags(),
                    PipelineAPI.getFileReaders(),
                    PromptsAPI.getAll(),
                ]);

                setModels(mdls);
                setFiles(fls);
                setFileTags(fTags);
                setFileReaders(fReaders.filter(r => r !== "upload"));
                setPrompts(prms);
            } catch (err) {
                console.error(err);
                alert("Error while fetching data: " + err);
            } finally {
                setLoadingModels(false);
                setLoadingFiles(false);
                setLoadingFileTags(false);
                setLoadingFileReaders(false);
                setLoadingPrompts(false);
            }
        };

        fetchData();
    }, [isOpen]);

    // ── Derived selection helpers ────────────────────────────────────────
    const byTagIds = new Set(
        files.filter(f => selectedFileTags.some(t => f.tags?.includes(t))).map(f => f.id)
    );
    const selectedFileCount = new Set([...byTagIds, ...selectedFileIds]).size;

    function filesSummary(): { value?: string; sub?: string } {
        if (selectedFileCount === 0) return {};
        const parts: string[] = [];
        if (selectedFileTags.length) parts.push(`Tags: ${selectedFileTags.join(", ")}`);
        if (selectedFileIds.length) parts.push(`${selectedFileIds.length} individual`);
        return {
            value: `${selectedFileCount} file${selectedFileCount !== 1 ? "s" : ""} selected`,
            sub: parts.join(" · "),
        };
    }

    function triggerShake(field: InvalidField) {
        setInvalid(prev => ({ ...prev, [field]: true }));
        setTimeout(() => setInvalid(prev => ({ ...prev, [field]: false })), 500);
    }

    function clearShake(field: InvalidField) {
        setInvalid(prev => ({ ...prev, [field]: false }));
    }

    // ── Navigation handlers ──────────────────────────────────────────────
    function goBack() {
        setView("main");
    }

    function selectModel(m: ModelInfo) {
        setSelectedModel(m);
        clearShake("model");
        goBack();
    }

    function selectPrompt(p: Prompt) {
        setSelectedPrompt(p);
        clearShake("prompt");
        goBack();
    }

    function selectFileReader(readerId: string) {
        setSelectedFileReader(readerId);
        clearShake("filereader");
        goBack();
    }

    function handleSetFileMode(mode: FileMode) {
        setFileMode(mode);
        if (mode === "reader") setView("filereader");
    }

    function toggleFileTag(tag: string) {
        setSelectedFileTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
    }

    function toggleFileId(id: number) {
        setSelectedFileIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
    }

    function activateParam(key: keyof ApiParams, value: number) {
        setApiParams(prev => ({ ...prev, [key]: value }));
    }

    function resetParam(key: keyof ApiParams) {
        setApiParams(prev => {
            const next = { ...prev };
            delete next[key];
            return next;
        });
    }

    function clearSample() {
        setSampleOutputText("");
        setSampleOutputSet(false);
    }

    function confirmSample() {
        if (sampleOutputText.length > 0) setSampleOutputSet(true);
        goBack();
    }

    function toggleSchedule() {
        setScheduleActive(prev => {
            const next = !prev;
            if (next) setProviderActive(false);
            return next;
        });
    }

    function toggleProviderBatch() {
        setProviderActive(prev => {
            const next = !prev;
            if (next) setScheduleActive(false);
            return next;
        });
    }

    // ── Validation ───────────────────────────────────────────────────────
    function validateSelections(): boolean {
        let valid = true;
        if (!selectedModel) { triggerShake("model"); valid = false; }
        if (selectedFileCount === 0) { triggerShake("files"); valid = false; }
        if (!selectedPrompt) { triggerShake("prompt"); valid = false; }
        if (fileMode === "reader" && !selectedFileReader) { triggerShake("filereader"); valid = false; }
        return valid;
    }

    function runEstimate() {
        if (!validateSelections()) return;
        alert("This feature is not yet implemented.");
    }

    function handleStart() {
        if (submitting) return;
        if (!validateSelections()) return;

        if (scheduleActive && !scheduledAt) {
            triggerShake("schedule");
            return;
        }

        const filesPayload = Array.from(new Set([...byTagIds, ...selectedFileIds]));
        const fileReaderPayload = fileMode === "upload" ? "upload" : (selectedFileReader as string);

        const payload: BatchStartRequest = {
            prompt_id: selectedPrompt!.id,
            files: filesPayload,
            endpoint_id: selectedModel!.endpoint_id,
            file_reader: fileReaderPayload,
            model: selectedModel!.model_name,
            temperature,
            json_format: jsonFormat,
            use_provider_batch: providerActive,
            batch_worker_settings: {
                max_tasks_per_minute: maxTasksPerMinute,
                max_parallel_tasks: maxParallelTasks,
                retries_per_failed_task: retriesPerFailedTask,
                failure_threshold_percent: failureThresholdPercent,
                queue_batch: queueBatch,
            },
        };

        if (scheduleActive && scheduledAt) {
            payload.scheduled_at = new Date(scheduledAt).toISOString();
        }

        setSubmitting(true);
        BatchesAPI.create(payload)
            .then((batch) => {
                onCreated(batch);
                onClose();
            })
            .catch((err) => {
                console.error(err);
                alert(err?.response?.data?.detail ?? err?.message ?? String(err));
            })
            .finally(() => setSubmitting(false));
    }

    const filesSum = filesSummary();

    return (
        <Modal isOpen={isOpen} onClose={onClose} className={styles.shell}>
            {view === "main" && (
                <MainView
                    selectedModel={selectedModel}
                    onOpenModel={() => setView("model")}
                    filesValue={filesSum.value}
                    filesSub={filesSum.sub}
                    onOpenFiles={() => setView("files")}
                    promptValue={selectedPrompt?.name}
                    promptSub={selectedPrompt ? (selectedPrompt.multi_prompt ? "Multi-step" : "1 step") : undefined}
                    onOpenPrompt={() => setView("prompt")}
                    fileMode={fileMode}
                    onSetFileMode={handleSetFileMode}
                    fileReaderValue={selectedFileReader ? prettifyReaderId(selectedFileReader) : undefined}
                    onOpenFileReader={() => setView("filereader")}
                    invalid={invalid}
                    modelSettingsOpen={modelSettingsOpen}
                    onToggleModelSettings={() => setModelSettingsOpen(v => !v)}
                    jsonFormat={jsonFormat}
                    onSetJsonFormat={setJsonFormat}
                    temperature={temperature}
                    onSetTemperature={setTemperature}
                    apiParams={apiParams}
                    onActivateParam={activateParam}
                    onResetParam={resetParam}
                    batchSettingsOpen={batchSettingsOpen}
                    onToggleBatchSettings={() => setBatchSettingsOpen(v => !v)}
                    maxTasksPerMinute={maxTasksPerMinute}
                    onSetMaxTasksPerMinute={setMaxTasksPerMinute}
                    maxParallelTasks={maxParallelTasks}
                    onSetMaxParallelTasks={setMaxParallelTasks}
                    retriesPerFailedTask={retriesPerFailedTask}
                    onSetRetriesPerFailedTask={setRetriesPerFailedTask}
                    failureThresholdPercent={failureThresholdPercent}
                    onSetFailureThresholdPercent={setFailureThresholdPercent}
                    queueBatch={queueBatch}
                    onSetQueueBatch={setQueueBatch}
                    intelligentBackoff={intelligentBackoff}
                    onSetIntelligentBackoff={setIntelligentBackoff}
                    estimateOpen={estimateOpen}
                    onToggleEstimate={() => setEstimateOpen(v => !v)}
                    onRunEstimate={runEstimate}
                    sampleOutputSet={sampleOutputSet}
                    onOpenSampleOutput={() => setView("sampleoutput")}
                    scheduleActive={scheduleActive}
                    onToggleSchedule={toggleSchedule}
                    providerActive={providerActive}
                    onToggleProviderBatch={toggleProviderBatch}
                    scheduledAt={scheduledAt}
                    onSetScheduledAt={setScheduledAt}
                    onStart={handleStart}
                    submitting={submitting}
                />
            )}

            {view === "model" && (
                <ModelView
                    models={models}
                    loading={loadingModels}
                    selectedModel={selectedModel}
                    search={modelSearch}
                    onSearchChange={setModelSearch}
                    onSelect={selectModel}
                    onBack={goBack}
                />
            )}

            {view === "files" && (
                <FilesView
                    files={files}
                    loading={loadingFiles || loadingFileTags}
                    fileTags={fileTags}
                    selectedFileTags={selectedFileTags}
                    selectedFileIds={selectedFileIds}
                    search={fileSearch}
                    onSearchChange={setFileSearch}
                    onToggleTag={toggleFileTag}
                    onToggleFile={toggleFileId}
                    onDone={goBack}
                />
            )}

            {view === "filereader" && (
                <FileReaderView
                    fileReaders={fileReaders}
                    loading={loadingFileReaders}
                    selectedFileReader={selectedFileReader}
                    onSelect={selectFileReader}
                    onBack={goBack}
                />
            )}

            {view === "sampleoutput" && (
                <SampleOutputView
                    text={sampleOutputText}
                    onTextChange={setSampleOutputText}
                    onClear={clearSample}
                    onConfirm={confirmSample}
                    onBack={goBack}
                />
            )}

            {view === "prompt" && (
                <PromptView
                    prompts={prompts}
                    loading={loadingPrompts}
                    selectedPrompt={selectedPrompt}
                    onSelect={selectPrompt}
                    onBack={goBack}
                />
            )}
        </Modal>
    );
}
