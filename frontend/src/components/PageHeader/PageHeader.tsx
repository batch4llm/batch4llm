import styles from "./PageHeader.module.css";

type Props = {
    title: string;
    subtitle: string;
    count: number;
    addLabel: string;
    onAdd: () => void;
};

export function PageHeader({ title, subtitle, count, addLabel, onAdd }: Props) {
    return (
        <div className={styles.header}>
            <div>
                <h2 className={styles.title}>
                    {title}
                    <span className={styles.count}>{count}</span>
                </h2>
                <p className={styles.subtitle}>{subtitle}</p>
            </div>
            <button className={styles.addBtn} type="button" onClick={onAdd}>
                <span className={styles.plus}>+</span>
                {addLabel}
            </button>
        </div>
    );
}
