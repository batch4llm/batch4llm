import styles from "./PageHeader.module.css";

type SecondaryAction = {
    label: string;
    onClick: () => void;
};

type Props = {
    title: string;
    subtitle: string;
    count: number;
    addLabel: string;
    onAdd: () => void;
    secondaryAction?: SecondaryAction;
};

export function PageHeader({ title, subtitle, count, addLabel, onAdd, secondaryAction }: Props) {
    return (
        <div className={styles.header}>
            <div>
                <h2 className={styles.title}>
                    {title}
                    <span className={styles.count}>{count}</span>
                </h2>
                <p className={styles.subtitle}>{subtitle}</p>
            </div>
            <div className={styles.actions}>
                {secondaryAction && (
                    <button className={styles.secondaryBtn} type="button" onClick={secondaryAction.onClick}>
                        {secondaryAction.label}
                    </button>
                )}
                <button className={styles.addBtn} type="button" onClick={onAdd}>
                    <span className={styles.plus}>+</span>
                    {addLabel}
                </button>
            </div>
        </div>
    );
}
