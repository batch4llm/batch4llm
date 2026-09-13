import { useEffect, useRef, useState } from "react";
import { PromptsAPI } from "../../api/prompts.ts";
import { type Prompt } from "../../types/Prompt.ts";
import { AddPromptModal } from "../../components/AddPromptModal/AddPromptModal";
import { PromptModal } from "../../components/PromptModal/PromptModal.tsx";
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

type ImportData = { name: string; content: string; multi_prompt: boolean };

export default function PromptsPage() {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [deleting, setDeleting] = useState<Prompt | null>(null);
    const [viewing, setViewing] = useState<Prompt | null>(null);
    const [clonePrompt, setClonePrompt] = useState<Prompt | null>(null);
    const [importData, setImportData] = useState<ImportData | null>(null);
    const importInputRef = useRef<HTMLInputElement>(null);

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

    function handleEditClone(prompt: Prompt) {
        setViewing(null);
        setClonePrompt(prompt);
    }

    function handleImportFile(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        e.target.value = "";
        if (!file) return;

        const isYaml = /\.ya?ml$/i.test(file.name);
        file.text().then((content) => {
            setImportData({
                name: file.name.replace(/\.[^/.]+$/, ""),
                content,
                multi_prompt: isYaml,
            });
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
                secondaryAction={{
                    label: "Import",
                    onClick: () => importInputRef.current?.click(),
                }}
            />

            <input
                type="file"
                accept=".txt,.yaml,.yml,text/plain,application/x-yaml"
                ref={importInputRef}
                onChange={handleImportFile}
                hidden
            />

            <div className={styles.grid}>
                {prompts.map(p => (
                    <PromptCard key={p.id} prompt={p} onView={setViewing} onDelete={setDeleting} />
                ))}
                <AddCard label="Add Prompt" onClick={() => setIsModalOpen(true)} />
            </div>

            <AddPromptModal
                isOpen={isModalOpen || !!clonePrompt || !!importData}
                onClose={() => { setIsModalOpen(false); setClonePrompt(null); setImportData(null); }}
                onCreated={(newPrompt: Prompt) =>
                    setPrompts(prev => [...prev, newPrompt])
                }
                initial={clonePrompt ? {
                    name: `${clonePrompt.name}_copy`,
                    content: clonePrompt.content,
                    multi_prompt: clonePrompt.multi_prompt,
                } : importData ?? undefined}
                title={importData ? "Import Prompt" : undefined}
            />

            <PromptModal
                prompt={viewing}
                onClose={() => setViewing(null)}
                onEditClone={handleEditClone}
            />

            <ConfirmDeleteModal
                prompt={deleting}
                onClose={() => setDeleting(null)}
                onConfirm={handleDelete}
            />
        </section>
    );
}
