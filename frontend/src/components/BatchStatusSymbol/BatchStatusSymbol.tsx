import styles from './BatchStatusSymbol.module.css';

type BatchStatusSymbolProps = {
    status: 'FAILED' | 'RUNNING' | 'COMPLETED' | string;
}

export function BatchStatusSymbol ({ status }: BatchStatusSymbolProps) {
    const getStatusClass = (status: string) => {
        switch (status) {
            case 'FAILED':
                return styles.statusFailed;
            case 'RUNNING':
                return styles.statusRunning;
            case 'COMPLETED':
                return styles.statusCompleted;
            default:
                return styles.statusUnknown;
        }
    };

    return (
        <span className={`${styles.statusPill} ${getStatusClass(status)}`}>
            {status.toLowerCase()}
        </span>
    );
}