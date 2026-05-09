import { Modal } from "../Modal/Modal.tsx";
import type { BatchFile } from "../../types/BatchFile.ts";
import styles from "./BatchFileModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    file: BatchFile;
};

export function BatchFileModal({ isOpen, onClose, file }: Props) {
    function jsonInterpreter(content: string) {
        try {
            const parsedOutput = JSON.parse(content);
            content = typeof parsedOutput === "string"
                ? parsedOutput
                : JSON.stringify(parsedOutput, null, 2);
        } catch {
        }
        return content;
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>{file.name}</h3>
            {file.costs_in_usd != null && <p>Kosten: {file.costs_in_usd} USD</p>}
            <p>Output:</p>
            {file.batch_tasks.map((batchTask, index) => (
                <div key={batchTask.id ?? index} className={styles.fileOutput}>
                    {batchTask.prompt_marker != null && <p>{batchTask.prompt_marker}</p>}
                    <pre>{jsonInterpreter(batchTask.output)}</pre>
                </div>
            ))
            }
        </Modal>
    );
}
