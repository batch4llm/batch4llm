import { PROVIDERS } from "../../../config/providers.ts";
import customLogo from "../../../assets/providers/custom.png";
import styles from "../AddEndpointModal.module.css";
import { IconBack } from "../Icons.tsx";
import type { Selected } from "../types.ts";

export type SubmitStatus = "idle" | "testing" | "creating";

type Props = {
    selected: Selected;
    name: string;
    onSetName: (v: string) => void;
    token: string;
    onSetToken: (v: string) => void;
    customProvider: string;
    onSetCustomProvider: (v: string) => void;
    customClient: string;
    onSetCustomClient: (v: string) => void;
    customUrl: string;
    onSetCustomUrl: (v: string) => void;
    status: SubmitStatus;
    error: string | null;
    isValid: boolean;
    onBack: () => void;
    onSubmit: () => void;
};

export function ProviderFormView({
    selected,
    name,
    onSetName,
    token,
    onSetToken,
    customProvider,
    onSetCustomProvider,
    customClient,
    onSetCustomClient,
    customUrl,
    onSetCustomUrl,
    status,
    error,
    isValid,
    onBack,
    onSubmit,
}: Props) {
    const isCustom = selected === "custom";
    const provider = isCustom ? null : PROVIDERS.find((p) => p.id === selected) ?? null;
    const busy = status !== "idle";

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack} disabled={busy}>
                    <IconBack /> Back
                </button>
                <div className={styles.viewHeaderProvider}>
                    <img src={provider?.image ?? customLogo} alt="" className={styles.viewHeaderLogo} />
                    <h2 className={styles.viewTitle}>{provider?.label ?? "Custom Endpoint"}</h2>
                </div>
            </div>

            <form className={styles.form} onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
                <div className={styles.fieldGroup}>
                    <label className={styles.label}>Name</label>
                    <input
                        className={styles.input}
                        type="text"
                        placeholder={isCustom ? "My Custom Endpoint" : `My ${provider?.label} endpoint`}
                        value={name}
                        minLength={3}
                        required
                        disabled={busy}
                        onChange={(e) => onSetName(e.target.value)}
                    />
                </div>

                {isCustom && (
                    <div className={styles.fieldRow}>
                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Provider</label>
                            <input
                                className={styles.input}
                                type="text"
                                placeholder="Self hosted"
                                value={customProvider}
                                required
                                disabled={busy}
                                onChange={(e) => onSetCustomProvider(e.target.value)}
                            />
                        </div>
                        <div className={styles.fieldGroup}>
                            <label className={styles.label}>Client</label>
                            <select
                                className={styles.select}
                                value={customClient}
                                disabled={busy}
                                onChange={(e) => onSetCustomClient(e.target.value)}
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
                )}

                {isCustom && (
                    <div className={styles.fieldGroup}>
                        <label className={styles.label}>Endpoint URL</label>
                        <input
                            className={styles.input}
                            type="url"
                            placeholder="https://your-api.example.com/v1"
                            value={customUrl}
                            disabled={busy}
                            onChange={(e) => onSetCustomUrl(e.target.value)}
                        />
                    </div>
                )}

                <div className={styles.fieldGroup}>
                    <label className={styles.label}>
                        {isCustom ? "Token" : "API Key"}
                        {isCustom && <span className={styles.optionalBadge}>optional</span>}
                    </label>
                    <input
                        className={styles.input}
                        type="password"
                        placeholder={isCustom ? "Bearer token or API key" : "sk-••••••••••••••••"}
                        value={token}
                        minLength={isCustom ? undefined : 3}
                        required={!isCustom}
                        disabled={busy}
                        onChange={(e) => onSetToken(e.target.value)}
                    />
                </div>

                {error && (
                    <div className={styles.errorBox}>
                        <div className={styles.errorBoxTitle}>Connection failed</div>
                        <div className={styles.errorBoxMessage}>{error}</div>
                    </div>
                )}

                <div className={styles.footer}>
                    <button type="submit" className={styles.btnPrimary} disabled={!isValid || busy}>
                        {status === "testing" ? "Testing connection…" : status === "creating" ? "Adding…" : "Add Endpoint"}
                    </button>
                </div>
            </form>
        </div>
    );
}
