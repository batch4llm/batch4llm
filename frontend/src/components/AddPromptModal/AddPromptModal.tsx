import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { ToggleSwitch } from "../ToggleSwitch/ToggleSwitch.tsx";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import styles from "./AddPromptModal.module.css";

type PromptMode = "simple" | "multi_step";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (prompt: Prompt) => void;
    initial?: { name: string; content: string; multi_prompt: boolean };
    title?: string;
};

const MODE_OPTIONS: [{ value: PromptMode; label: string }, { value: PromptMode; label: string }] = [
    { value: "simple", label: "Simple" },
    { value: "multi_step", label: "Multi Step" },
];

const MULTI_STEP_TEMPLATE = `multi_prompt_v1:
  pre: ""
  post: ""
  tasks:
    - id: step_1
      prompt: |
        Write the prompt for this step here...
`;

function modeOf(initial?: { multi_prompt: boolean }): PromptMode {
    return initial?.multi_prompt ? "multi_step" : "simple";
}

export function AddPromptModal({ isOpen, onClose, onCreated, initial, title }: Props) {
    const [name, setName] = useState(initial?.name ?? "");
    const [content, setContent] = useState(initial?.content ?? "");
    const [mode, setMode] = useState<PromptMode>(modeOf(initial));

    // Re-fill the form whenever the modal is (re-)opened, so a new `initial`
    // (e.g. cloning a different prompt) is picked up without resetting the
    // fields while the user is still typing in an already-open modal.
    const [wasOpen, setWasOpen] = useState(isOpen);
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) {
            setName(initial?.name ?? "");
            setContent(initial?.content ?? "");
            setMode(modeOf(initial));
        }
    }

    function handleModeChange(newMode: PromptMode) {
        setMode(newMode);
        // Give the user a pre-filled YAML skeleton so they know which
        // values to set, but never overwrite something they've already typed.
        if (newMode === "multi_step" && content.trim() === "") {
            setContent(MULTI_STEP_TEMPLATE);
        }
    }

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        PromptsAPI.create({
            name: name,
            content: content,
            multi_prompt: mode === "multi_step"
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

    return (
        <Modal isOpen={isOpen} onClose={onClose} className={styles.modal}>
            <h3>{title ?? (initial ? "Clone Prompt" : "Add Prompt")}</h3>

            <form onSubmit={handleSubmit} className={styles.promptForm}>
                <input
                    type="text"
                    placeholder="Name"
                    required
                    minLength={3}
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />

                <ToggleSwitch
                    options={MODE_OPTIONS}
                    value={mode}
                    onChange={handleModeChange}
                />

                <textarea
                    placeholder={mode === "multi_step" ? "multi_prompt_v1:\n  tasks:\n    - id: step_1\n      prompt: ..." : "Write your prompt here..."}
                    className={mode === "multi_step" ? styles.yamlTextarea : undefined}
                    minLength={3}
                    rows={mode === "multi_step" ? 14 : 10}
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                />

                <button type="submit">Add</button>
            </form>
        </Modal>
    );
}
