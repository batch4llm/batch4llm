import styles from "./AddCard.module.css";

type Props = {
    label: string;
    onClick: () => void;
};

export function AddCard({ label, onClick }: Props) {
    return (
        <button className={styles.card} type="button" onClick={onClick}>
            <span className={styles.plus}>+</span>
            {label}
        </button>
    );
}
