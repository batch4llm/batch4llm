import { useEffect, useState } from "react";
import { PromptsAPI } from "../../api/prompts.ts";
import { type Prompt } from "../../types/Prompt.ts";
import { AddPromptModal } from "../../components/AddPromptModal/AddPromptModal";
import { PageHeader } from "../../components/PageHeader/PageHeader.tsx";
import { PromptCard } from "../../components/PromptCard/PromptCard.tsx";
import { AddCard } from "../../components/AddCard/AddCard.tsx";
import styles from "./PromptsPage.module.css";

export default function PromptsPage() {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    useEffect(() => {
        PromptsAPI.getAll().then(setPrompts);
    }, []);

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
                    <PromptCard key={p.id} prompt={p} />
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
        </section>
    );
}
