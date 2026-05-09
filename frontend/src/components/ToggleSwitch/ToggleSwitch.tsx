import styles from "./ToggleSwitch.module.css";

type Option<T extends string> = {
    value: T;
    label: string;
};

type Props<T extends string> = {
    options: [Option<T>, Option<T>];
    value: T;
    onChange: (value: T) => void;
};

export function ToggleSwitch<T extends string>({ options, value, onChange }: Props<T>) {
    const activeIndex = options.findIndex((o) => o.value === value);

    return (
        <div className={styles.toggleWrapper}>
            {options.map((option) => (
                <button
                    key={option.value}
                    className={`${styles.toggleBtn} ${value === option.value ? styles.toggleActive : ""}`}
                    onClick={() => onChange(option.value)}
                    type="button"
                >
                    {option.label}
                </button>
            ))}
            <div
                className={styles.toggleIndicator}
                style={{
                    transform: activeIndex === 1 ? "translateX(100%)" : "translateX(0)",
                }}
            />
        </div>
    );
}