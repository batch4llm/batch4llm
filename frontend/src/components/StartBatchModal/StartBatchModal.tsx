import { useState, useEffect } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { BatchesAPI } from "../../api/batches.ts";
import { EndpointsAPI } from "../../api/endpoints.ts";
import { PipelineAPI } from "../../api/pipeline.ts";
import { FilesAPI } from "../../api/files.ts";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import type { Batch } from "../../types/Batch.ts";
import styles from "./StartBatchModal.module.css"
import type {Endpoint} from "../../types/Endpoint.ts";


type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (batch: Batch) => void;
};

export function StartBatchModal({ isOpen, onClose, onCreated }: Props) {
    const [endpointId, setEndpointId] = useState<number | null>(null);
    const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
    const [loadingEndpoints, setLoadingEndpoints] = useState(false);

    const [fileTag, setFileTag] = useState("");
    const [fileTags, setFileTags] = useState<string[]>([]);
    const [loadingFileTags, setLoadingFileTags] = useState(false);

    const [fileReader, setFileReader] = useState("");
    const [fileReaders, setFileReaders] = useState<string[]>([]);
    const [loadingFileReaders, setLoadingFileReaders] = useState(false);

    const [jsonFormat, setJSONFormat] = useState("False");

    const [model, setModel] = useState("");
    const [models, setModels] = useState<string[]>([]);
    const [loadingModels, setLoadingModels] = useState(false);

    const [promptId, setPromptId] = useState<number | null>(null);
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [loadingPrompts, setLoadingPrompts] = useState(false);

    const [temperature, setTemperature] = useState<number>(1);

    // Advanced batch settings
    const [advancedOpen, setAdvancedOpen] = useState(false);
    const [maxTasksPerMinute, setMaxTasksPerMinute] = useState<number>(5);
    const [maxParallelTasks, setMaxParallelTasks] = useState<number>(1);
    const [retriesPerFailedTask, setRetriesPerFailedTask] = useState<number>(2);
    const [maxRetries, setMaxRetries] = useState<number>(5);
    const [queueBatch, setQueueBatch] = useState<boolean>(true);

    // Advanced model settings
    const [advancedModelOpen, setAdvancedModelOpen] = useState(false);

    useEffect(() => {
        if (!endpointId) {
            setModels([]);
            setModel("");
            return;
        }

        const loadModels = async () => {
            setLoadingModels(true);
            try {
                const mdls = await EndpointsAPI.getModels(endpointId);
                setModels(mdls);
            } catch (err) {
                console.error(err);
                alert("Error loading models: " + err);
            } finally {
                setLoadingModels(false);
            }
        };

        loadModels();
    }, [endpointId]);


    useEffect(() => {
        if (!isOpen) return;

        const fetchData = async () => {
            setLoadingEndpoints(true);
            setLoadingFileTags(true);
            setLoadingFileReaders(true);
            setLoadingPrompts(true);

            try {
                const [eps, fTags, fReaders, prms] = await Promise.all([
                    EndpointsAPI.getAll(),
                    FilesAPI.getFileTags(),
                    PipelineAPI.getFileReaders(),
                    PromptsAPI.getAll(),
                ]);

                setEndpoints(eps);
                setFileTags(fTags);
                setFileReaders(fReaders);
                setPrompts(prms);
            } catch (err) {
                console.error(err);
                alert("Error while fetching data: " + err);
            } finally {
                setLoadingEndpoints(false);
                setLoadingFileTags(false);
                setLoadingFileReaders(false);
                setLoadingModels(false);
                setLoadingPrompts(false);
            }
        };

        fetchData();
    }, [isOpen]);


    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        FilesAPI.getFilesByTag(fileTag).then(r => {
            let files = r.map(f => f.id)

            if (promptId === null) {
                alert("Please select a prompt");
                return;
            }
            if (endpointId === null) {
                alert("Please select a endpoint");
                return;
            }

            BatchesAPI.create({
                prompt_id: promptId,
                files: files,
                endpoint_id: endpointId,
                file_reader: fileReader,
                model: model,
                temperature: temperature,
                json_format: jsonFormat === "True",
                batch_worker_settings: {
                    max_tasks_per_minute: maxTasksPerMinute,
                    max_parallel_tasks: maxParallelTasks,
                    retries_per_failed_task: retriesPerFailedTask,
                    max_retries: maxRetries,
                    queue_batch: queueBatch,
                }
            }).then((data) => {
                onCreated(data)
            }).catch(error => {
                console.error(error);
                alert(error.detail);
            })
        })

        onClose();
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>Start Batch</h3>

            <form onSubmit={handleSubmit} className={styles.batchStartForm}>

                <label>Endpoint</label>
                <select
                    required
                    value={endpointId ?? ""}
                    onChange={(e) => setEndpointId(parseInt(e.target.value))}
                    disabled={loadingEndpoints}
                >
                    <option value="" disabled>
                        {loadingEndpoints ? "Loading..." : "Please select"}
                    </option>
                    {endpoints.map((ep) => (
                        <option key={ep.id} value={ep.id}>
                            {ep.name}
                        </option>
                    ))}
                </select>

                <label>Model</label>
                <select
                    required
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    disabled={!endpointId || loadingModels}
                >
                    <option value="" disabled>
                        {!endpointId
                            ? "Select endpoint first"
                            : loadingModels
                                ? "Loading..."
                                : "Please select"}
                    </option>
                    {models.map((md) => (
                        <option key={md} value={md}>
                            {md.replace("models/", "")}
                        </option>
                    ))}
                </select>

                <label>File-Tag</label>
                <select
                    required
                    value={fileTag}
                    onChange={(e) => setFileTag(e.target.value)}
                >
                    <option value="" disabled>
                        {loadingFileTags ? "Loading..." : "Please select"}
                    </option>
                    {fileTags.map((ft) => (
                        <option key={ft} value={ft}>
                            {ft}
                        </option>
                    ))}
                </select>

                <label>File Reader</label>
                <select
                    required
                    value={fileReader}
                    onChange={(e) => setFileReader(e.target.value)}
                >
                    <option value="" disabled>
                        {loadingFileReaders ? "Loading..." : "Please select"}
                    </option>
                    {fileReaders.map((fr) => (
                        <option key={fr} value={fr}>
                            {fr}
                        </option>
                    ))}
                </select>

                <label>Prompt</label>
                <select
                    required
                    value={promptId ?? ""}
                    onChange={(e) => setPromptId(parseInt(e.target.value))}
                >
                    <option value="" disabled>
                        {loadingPrompts ? "Loading..." : "Please select"}
                    </option>
                    {prompts.map((pr) => (
                        <option key={pr.id} value={pr.id}>
                            {pr.name}
                        </option>
                    ))}
                </select>


                {/* Model Settings */}
                <div className={styles.advancedSection}>
                    <button
                        type="button"
                        className={styles.advancedToggle}
                        onClick={() => setAdvancedModelOpen(prev => !prev)}
                    >
                        <span className={`${styles.advancedArrow} ${advancedOpen ? styles.advancedArrowOpen : ""}`}>
                            ▶
                        </span>
                        Model Settings
                    </button>

                    {advancedModelOpen && (
                        <div className={styles.advancedFields}>
                            <label>Temperature</label>
                            <input
                                id="temperature-input"
                                placeholder="Temperature"
                                required
                                type="number"
                                value={temperature} min="0.0" max="3.0"
                                step="0.1"
                                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                            />

                            <label>Answer Format</label>
                            <select
                                required
                                value={jsonFormat}
                                onChange={(e) => setJSONFormat(e.target.value)}
                            >
                                <option value="True">JSON</option>
                                <option value="False">Text</option>
                            </select>
                        </div>
                    )}
                </div>

                {/* Batch Settings */}
                <div className={styles.advancedSection}>
                    <button
                        type="button"
                        className={styles.advancedToggle}
                        onClick={() => setAdvancedOpen(prev => !prev)}
                    >
                        <span className={`${styles.advancedArrow} ${advancedOpen ? styles.advancedArrowOpen : ""}`}>
                            ▶
                        </span>
                        Batch Settings
                    </button>

                    {advancedOpen && (
                        <div className={styles.advancedFields}>
                            <label>Max Tasks per Minute</label>
                            <input
                                type="number"
                                required
                                min={1} max={20}
                                value={maxTasksPerMinute}
                                onChange={(e) => setMaxTasksPerMinute(parseInt(e.target.value))}
                            />

                            <label>Max Parallel Tasks</label>
                            <input
                                type="number"
                                required
                                min={1} max={20}
                                value={maxParallelTasks}
                                onChange={(e) => setMaxParallelTasks(parseInt(e.target.value))}
                            />

                            <label>Retries per Failed Task</label>
                            <input
                                type="number"
                                required
                                min={0} max={20}
                                value={retriesPerFailedTask}
                                onChange={(e) => setRetriesPerFailedTask(parseInt(e.target.value))}
                            />

                            <label>Max Retries</label>
                            <input
                                type="number"
                                required
                                min={0} max={20}
                                value={maxRetries}
                                onChange={(e) => setMaxRetries(parseInt(e.target.value))}
                            />

                            <label>Queue Batch</label>
                            <select
                                value={queueBatch ? "true" : "false"}
                                onChange={(e) => setQueueBatch(e.target.value === "true")}
                            >
                                <option value="true">Yes</option>
                                <option value="false">No</option>
                            </select>
                        </div>
                    )}
                </div>

                <button type="submit">Start</button>
            </form>
        </Modal>
    );
}