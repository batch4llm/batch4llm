import type { ModelInfo } from "../../../types/Model";
import { logoFor } from "../../../utils/providerLogo";
import { fmtCost } from "../formatCost.ts";
import styles from "../StartBatchModal.module.css";
import { IconBack, IconCheck, IconSearch } from "../Icons.tsx";

type Props = {
    models: ModelInfo[];
    loading: boolean;
    selectedModel: ModelInfo | null;
    search: string;
    onSearchChange: (value: string) => void;
    onSelect: (model: ModelInfo) => void;
    onBack: () => void;
};

export function ModelView({ models, loading, selectedModel, search, onSearchChange, onSelect, onBack }: Props) {
    const q = search.toLowerCase();
    const filtered = models.filter(m =>
        !q ||
        m.model_name.toLowerCase().includes(q) ||
        m.endpoint_name.toLowerCase().includes(q) ||
        m.provider.toLowerCase().includes(q)
    );

    return (
        <div className={styles.view}>
            <div className={styles.viewHeader}>
                <button type="button" className={styles.backBtn} onClick={onBack}>
                    <IconBack /> Back
                </button>
                <h2 className={styles.viewTitle}>Select Model</h2>
                {selectedModel && <span className={styles.badgeSelected}>{selectedModel.model_name}</span>}
            </div>

            <div className={styles.searchWrap}>
                <span className={styles.searchIcon}><IconSearch /></span>
                <input
                    type="text"
                    className={styles.searchInput}
                    placeholder="Search models, providers..."
                    value={search}
                    onChange={(e) => onSearchChange(e.target.value)}
                />
            </div>

            <div className={styles.modelGrid}>
                {loading && <div className={styles.emptyNote}>Loading...</div>}
                {!loading && filtered.length === 0 && <div className={styles.emptyNote}>No models found.</div>}
                {filtered.map((m) => {
                    const selected = selectedModel?.id === m.id;
                    return (
                        <button
                            type="button"
                            key={m.id}
                            className={`${styles.modelTile}${selected ? ` ${styles.selected}` : ""}`}
                            onClick={() => onSelect(m)}
                        >
                            <div className={styles.providerBadge}>
                                <img src={logoFor(m.provider)} alt="" />
                            </div>
                            <div className={styles.modelInfo}>
                                <div className={styles.modelName}>{m.model_name}</div>
                                <div className={styles.modelEndpoint}>{m.endpoint_name}</div>
                                <div className={styles.modelCost}>
                                    In ${fmtCost(m.input_cost_per_1m_tokens)} · Out ${fmtCost(m.output_cost_per_1m_tokens)}
                                </div>
                                <div className={styles.modelCostUnit}>per 1M tokens</div>
                            </div>
                            {selected && <span className={styles.checkIcon}><IconCheck /></span>}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
