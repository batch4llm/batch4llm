import { PROVIDERS } from "../../../config/providers.ts";
import customLogo from "../../../assets/providers/custom.png";
import styles from "../AddEndpointModal.module.css";
import { IconChevronRight } from "../Icons.tsx";
import type { Selected } from "../types.ts";

type Props = {
    onSelect: (selected: Selected) => void;
};

export function ProviderSelectView({ onSelect }: Props) {
    return (
        <div className={styles.view}>
            <h2 className={styles.viewTitle}>Add Endpoint</h2>
            <p className={styles.viewSub}>Choose the provider you want to connect.</p>

            <div className={styles.providerList}>
                {PROVIDERS.map((p) => (
                    <button
                        key={p.id}
                        type="button"
                        className={styles.providerRow}
                        onClick={() => onSelect(p.id)}
                    >
                        <span className={styles.providerRowLogo}>
                            <img src={p.image} alt="" />
                        </span>
                        <span className={styles.providerRowLabel}>{p.label}</span>
                        <IconChevronRight />
                    </button>
                ))}
                <button
                    type="button"
                    className={styles.providerRow}
                    onClick={() => onSelect("custom")}
                >
                    <span className={styles.providerRowLogo}>
                        <img src={customLogo} alt="" />
                    </span>
                    <span className={styles.providerRowLabel}>Custom</span>
                    <IconChevronRight />
                </button>
            </div>
        </div>
    );
}
