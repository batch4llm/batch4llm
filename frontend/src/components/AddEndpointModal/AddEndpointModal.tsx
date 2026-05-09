import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { ToggleSwitch } from "../ToggleSwitch/ToggleSwitch.tsx";
import { EndpointsAPI } from "../../api/endpoints.ts";
import type { Endpoint } from "../../types/Endpoint.ts";
import { PROVIDERS } from "../../config/providers.ts";
import styles from "./AddEndpointModal.module.css";

type Mode = "provider" | "custom";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (endpoint: Endpoint) => void;
};

const MODE_OPTIONS: [{ value: Mode; label: string }, { value: Mode; label: string }] = [
    { value: "provider", label: "Provider" },
    { value: "custom", label: "Custom" },
];

export function AddEndpointModal({ isOpen, onClose, onCreated }: Props) {
    const [mode, setMode] = useState<Mode>("provider");

    // Provider mode state
    const [selectedProvider, setSelectedProvider] = useState<number | null>(null);
    const [providerName, setProviderName] = useState("");
    const [providerToken, setProviderToken] = useState("");

    // Custom mode state
    const [customName, setCustomName] = useState("");
    const [customProvider, setCustomProvider] = useState("Self hosted");
    const [customClient, setCustomClient] = useState("openai");
    const [customUrl, setCustomUrl] = useState("");
    const [customToken, setCustomToken] = useState("");

    function buildPayload(): Record<string, string> {
        if (mode === "provider") {
            const prov = PROVIDERS.find((p) => p.id === selectedProvider);
            return {
                name: providerName,
                client: prov?.client ?? "",
                provider: prov?.provider ?? "",
                ...(prov?.url ? { url: prov.url } : {}),
                ...(providerToken ? { token: providerToken } : {}),
            };
        } else {
            return {
                name: customName,
                client: customClient,
                provider: customProvider,
                ...(customUrl ? { url: customUrl } : {}),
                ...(customToken ? { token: customToken } : {}),
            };
        }
    }

    function handleTest() {
        const payload = buildPayload();
        EndpointsAPI.test?.(payload)
            .then((data) => {
                if (data.success) {
                    alert("Successfully test");
                }
                else {
                    alert(`Connection failed: ${data.error}`)
                }
            })
            .catch((err: unknown) => alert(`Health check failed: ${err}`));
    }

    function handleAdd() {
        const payload = buildPayload();
        EndpointsAPI.create(payload)
            .then((data) => {
                onCreated(data);
                onClose();
            })
            .catch((err: unknown) => alert(err));
    }

    const isProviderFormValid =
        mode === "provider" && selectedProvider !== null && providerName.length >= 3;

    const isCustomFormValid =
        mode === "custom" && customName.length >= 3 && customProvider.length >= 1;

    const isValid = isProviderFormValid || isCustomFormValid;

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <div className={styles.container}>
                {/* Header */}
                <div className={styles.header}>
                    <h3 className={styles.title}>Add Endpoint</h3>
                    <p className={styles.subtitle}>Connect a new AI provider to your workspace</p>
                </div>

                {/* Toggle */}
                <ToggleSwitch
                    options={MODE_OPTIONS}
                    value={mode}
                    onChange={setMode}
                />

                {/* Provider Mode */}
                {mode === "provider" && (
                    <div className={styles.section}>
                        <div className={styles.providerGrid}>
                            {PROVIDERS.map((p) => (
                                <button
                                    key={p.id}
                                    type="button"
                                    className={`${styles.providerCard} ${selectedProvider === p.id ? styles.providerCardSelected : ""}`}
                                    onClick={() => setSelectedProvider(p.id)}
                                >
                                    <div className={styles.providerImageBox}>
                                        <img
                                            src={p.image}
                                            alt={p.label}
                                            className={styles.providerImage}
                                        />
                                    </div>
                                    <span className={styles.providerLabel}>{p.label}</span>
                                </button>
                            ))}
                        </div>

                        <div className={styles.fieldRow}>
                            <div className={styles.fieldGroup}>
                                <label className={styles.label}>Name</label>
                                <input
                                    className={styles.input}
                                    type="text"
                                    placeholder="My OpenAI endpoint"
                                    value={providerName}
                                    minLength={3}
                                    onChange={(e) => setProviderName(e.target.value)}
                                />
                            </div>
                            <div className={styles.fieldGroup}>
                                <label className={styles.label}>API Key</label>
                                <input
                                    className={styles.input}
                                    type="password"
                                    placeholder="sk-••••••••••••••••"
                                    value={providerToken}
                                    onChange={(e) => setProviderToken(e.target.value)}
                                />
                            </div>
                        </div>
                    </div>
                )}

                {/* Custom Mode */}
                {mode === "custom" && (
                    <div className={styles.section}>
                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Name</label>
                            <input
                                className={styles.input}
                                type="text"
                                placeholder="My Custom Endpoint"
                                value={customName}
                                minLength={3}
                                onChange={(e) => setCustomName(e.target.value)}
                            />
                        </div>

                        <div className={styles.fieldRow}>
                            <div className={styles.fieldGroup}>
                                <label className={styles.label}>Provider</label>
                                <input
                                    className={styles.input}
                                    type="text"
                                    placeholder="Self hosted"
                                    value={customProvider}
                                    onChange={(e) => setCustomProvider(e.target.value)}
                                />
                            </div>
                            <div className={styles.fieldGroup}>
                                <label className={styles.label}>Client</label>
                                <select
                                    className={styles.select}
                                    value={customClient}
                                    onChange={(e) => setCustomClient(e.target.value)}
                                >
                                    <option value="openai">OpenAI-compatible</option>
                                    <option value="gemini">Gemini</option>
                                    <option value="anthropic">Anthropic</option>
                                    <option value="mistral">Mistral</option>
                                    <option value="ollama">Ollama</option>
                                    <option value="test">Test-Client</option>
                                </select>
                            </div>
                        </div>

                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Endpoint URL</label>
                            <input
                                className={styles.input}
                                type="url"
                                placeholder="https://your-api.example.com/v1"
                                value={customUrl}
                                onChange={(e) => setCustomUrl(e.target.value)}
                            />
                        </div>

                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>
                                Token
                                <span className={styles.optionalBadge}>optional</span>
                            </label>
                            <input
                                className={styles.input}
                                type="password"
                                placeholder="Bearer token or API key"
                                value={customToken}
                                onChange={(e) => setCustomToken(e.target.value)}
                            />
                        </div>
                    </div>
                )}

                {/* Footer Actions */}
                <div className={styles.footer}>
                    <button
                        className={styles.btnSecondary}
                        type="button"
                        onClick={handleTest}
                        disabled={!isValid}
                    >
                        Test Connection
                    </button>
                    <button
                        className={styles.btnPrimary}
                        type="button"
                        onClick={handleAdd}
                        disabled={!isValid}
                    >
                        Add Endpoint
                    </button>
                </div>
            </div>
        </Modal>
    );
}