import { useEffect, useState } from "react";
import { PromptsAPI } from "../../api/prompts.ts";
import { type Prompt } from "../../types/Prompt.ts";
import { AddPromptModal } from "../../components/AddPromptModal/AddPromptModal";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import { PromptCard } from "../../components/PromptCard/PromptCard.tsx";
import { AddCard } from "../../components/AddCard/AddCard.tsx";
import { Modal } from "../../components/Modal/Modal.tsx";
import styles from "./PromptsPage.module.css";

// ── Confirm Delete Modal ────────────────────────────────────────
type DeleteModalProps = {
    prompt: Prompt | null;
    onClose: () => void;
    onConfirm: (id: number) => void;
};

function ConfirmDeleteModal({ prompt, onClose, onConfirm }: DeleteModalProps) {
    if (!prompt) return null;
    return (
        <Modal isOpen onClose={onClose} className={styles.narrowModal}>
            <h3 className={styles.confirmTitle}>Delete prompt?</h3>
            <p className={styles.confirmBody}>
                <strong>{prompt.name}</strong> will be permanently removed. Batches that
                already used it keep showing its name, but this cannot be undone.
            </p>
            <div className={styles.confirmActions}>
                <button className={styles.btnSecondary} onClick={onClose}>Cancel</button>
                <button className={styles.btnDanger} onClick={() => { onConfirm(prompt.id); onClose(); }}>Delete</button>
            </div>
        </Modal>
    );
}

export default function PromptsPage() {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleting, setDeleting] = useState<Prompt | null>(null);

    useEffect(() => {
        PromptsAPI.getAll().then(setPrompts);
    }, []);

    function handleDelete(id: number) {
        PromptsAPI.delete(id)
            .then(() => setPrompts(prev => prev.filter(p => p.id !== id)))
            .catch((err) => {
                const detail = err?.response?.data?.detail;
                alert(detail || "Prompt could not be deleted.");
            });
    }

    return (
        <section>
            <PageHeader
                title="Prompts"
                subtitle="Reusable instructions you can attach to a batch. Multi-prompts are split into separate model requests when run."
                count={prompts.length}
                addLabel="Add Prompt"
                onAdd={() => setIsModalOpen(true)}
            />

            <div className={styles.grid}>
                {prompts.map(p => (
                    <PromptCard key={p.id} prompt={p} onDelete={setDeleting} />
                ))}
                <AddCard label="Add Prompt" onClick={() => setIsModalOpen(true)} />
            </div>

            <AddPromptModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onCreated={(newPrompt: Prompt) =>
                    setPrompts(prev => [...prev, newPrompt])
                }
            />

            <ConfirmDeleteModal
                prompt={deleting}
                onClose={() => setDeleting(null)}
                onConfirm={handleDelete}
            />
        </section>
    );
}
