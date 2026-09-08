import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import styles from "./AddPromptModal.module.css";


type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (prompt: Prompt) => void;
    initial?: { name: string; content: string; multi_prompt: boolean };
};

export function AddPromptModal({ isOpen, onClose, onCreated, initial }: Props) {
    const [name, setName] = useState(initial?.name ?? "");
    const [content, setContent] = useState(initial?.content ?? "");
    const [isMultiPrompt, setIsMultiPrompt] = useState(initial?.multi_prompt ?? false);

    // Re-fill the form whenever the modal is (re-)opened, so a new `initial`
    // (e.g. cloning a different prompt) is picked up without resetting the
    // fields while the user is still typing in an already-open modal.
    const [wasOpen, setWasOpen] = useState(isOpen);
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) {
            setName(initial?.name ?? "");
            setContent(initial?.content ?? "");
            setIsMultiPrompt(initial?.multi_prompt ?? false);
        }
    }

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        PromptsAPI.create({
            name: name,
            content: content,
            multi_prompt: isMultiPrompt
        }).then((data) => {
            onCreated(data);
            console.log(data);
        }).catch((err) => {
            console.log(err);
            alert(err);
        })

        console.log({ name, content });

        onClose();
    }

    function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
        const file = e.target.files?.[0];
        if (!file) return;

        setName(file.name);
        file.text().then(setContent);
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose}>
            <h3>{initial ? "Clone Prompt" : "Add Prompt"}</h3>

            <div className={styles.fileUpload}>
                Upload .txt file
                <input
                    type="file"
                    accept="text/plain"
                    onChange={handleFileUpload}
                />
            </div>

            <p className={styles.separator}>— or —</p>

            <form onSubmit={handleSubmit} className={styles.promptForm}>
                <input
                    type="text"
                    placeholder="Name"
                    required
                    minLength={3}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />

                <textarea
                    placeholder="Write your prompt here..."
                    minLength={3}
                    rows={10}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                />

                <label>
                    <input
                        type="checkbox"
                        checked={isMultiPrompt}
                        onChange={(e) => setIsMultiPrompt(e.target.checked)}
                    />
                    Multi Prompt (interpreter)
                </label>

                <button type="submit">Add</button>
            </form>
        </Modal>
    );
}
