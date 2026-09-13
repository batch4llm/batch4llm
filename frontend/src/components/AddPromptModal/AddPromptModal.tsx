import { useState } from "react";
import { Modal } from "../Modal/Modal.tsx";
import { PromptsAPI } from "../../api/prompts.ts";
import type { Prompt } from "../../types/Prompt.ts";
import { structuredToYaml, yamlToStructured, type PromptTask } from "../../utils/multiPromptYaml.ts";
import type { Step } from "./types.ts";
import { TypeSelectView } from "./views/TypeSelectView.tsx";
import { SimpleView } from "./views/SimpleView.tsx";
import { ComplexTypeSelectView } from "./views/ComplexTypeSelectView.tsx";
import { ComplexYamlView } from "./views/ComplexYamlView.tsx";
import { ComplexVisualView } from "./views/ComplexVisualView.tsx";
import styles from "./AddPromptModal.module.css";

type Props = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (prompt: Prompt) => void;
    initial?: { name: string; content: string; multi_prompt: boolean };
    title?: string;
};

const MULTI_STEP_TEMPLATE = `multi_prompt_v1:
  pre: ""
  post: ""
  tasks:
    - id: step_1
      prompt: |
        Write the prompt for this step here...
`;

type FormState = {
    step: Step;
    name: string;
    simpleContent: string;
    yamlContent: string;
    pre: string;
    post: string;
    tasks: PromptTask[];
};

function initialFormState(initial?: Props["initial"]): FormState {
    const base: FormState = {
        step: "type-select",
        name: initial?.name ?? "",
        simpleContent: "",
        yamlContent: MULTI_STEP_TEMPLATE,
        pre: "",
        post: "",
        tasks: [{ id: "step_1", prompt: "" }],
    };

    if (!initial) return base;
    if (!initial.multi_prompt) {
        return { ...base, step: "simple", simpleContent: initial.content };
    }

    const structured = yamlToStructured(initial.content);
    if (structured) {
        return { ...base, step: "complex-visual", pre: structured.pre, post: structured.post, tasks: structured.tasks };
    }
    return { ...base, step: "complex-yaml", yamlContent: initial.content };
}

export function AddPromptModal({ isOpen, onClose, onCreated, initial, title }: Props) {
    const [form, setForm] = useState<FormState>(() => initialFormState(initial));

    // Re-fill the form whenever the modal is (re-)opened, so a new `initial`
    // (e.g. cloning a different prompt) is picked up without resetting the
    // fields while the user is still typing in an already-open modal.
    const [wasOpen, setWasOpen] = useState(isOpen);
    if (isOpen !== wasOpen) {
        setWasOpen(isOpen);
        if (isOpen) setForm(initialFormState(initial));
    }

    function update(patch: Partial<FormState>) {
        setForm(prev => ({ ...prev, ...patch }));
    }

    function handleSwitchToVisual() {
        const structured = yamlToStructured(form.yamlContent);
        if (!structured) return;
        update({ step: "complex-visual", pre: structured.pre, post: structured.post, tasks: structured.tasks });
    }

    function handleSwitchToYaml() {
        update({ step: "complex-yaml", yamlContent: structuredToYaml({ pre: form.pre, post: form.post, tasks: form.tasks }) });
    }

    function handleSubmit() {
        const content = form.step === "complex-visual"
            ? structuredToYaml({ pre: form.pre, post: form.post, tasks: form.tasks })
            : form.step === "complex-yaml" ? form.yamlContent : form.simpleContent;
        const multi_prompt = form.step === "complex-yaml" || form.step === "complex-visual";

        PromptsAPI.create({ name: form.name, content, multi_prompt })
            .then((data) => onCreated(data))
            .catch((err) => alert(err));

        onClose();
    }

    return (
        <Modal isOpen={isOpen} onClose={onClose} className={styles.modal}>
            {renderStep()}
        </Modal>
    );

    function renderStep() {
        switch (form.step) {
            case "type-select":
                return (
                    <TypeSelectView
                        onSelectSimple={() => update({ step: "simple" })}
                        onSelectComplex={() => update({ step: "complex-select" })}
                    />
                );
            case "simple":
                return (
                    <SimpleView
                        title={title}
                        name={form.name}
                        onSetName={(v) => update({ name: v })}
                        content={form.simpleContent}
                        onSetContent={(v) => update({ simpleContent: v })}
                        onBack={() => update({ step: "type-select" })}
                        onSubmit={handleSubmit}
                    />
                );
            case "complex-select":
                return (
                    <ComplexTypeSelectView
                        onBack={() => update({ step: "type-select" })}
                        onSelectYaml={() => update({ step: "complex-yaml" })}
                        onSelectVisual={() => update({ step: "complex-visual" })}
                    />
                );
            case "complex-yaml":
                return (
                    <ComplexYamlView
                        title={title}
                        name={form.name}
                        onSetName={(v) => update({ name: v })}
                        content={form.yamlContent}
                        onSetContent={(v) => update({ yamlContent: v })}
                        canSwitchToVisual={yamlToStructured(form.yamlContent) !== null}
                        onSwitchToVisual={handleSwitchToVisual}
                        onBack={() => update({ step: "complex-select" })}
                        onSubmit={handleSubmit}
                    />
                );
            case "complex-visual":
                return (
                    <ComplexVisualView
                        title={title}
                        name={form.name}
                        onSetName={(v) => update({ name: v })}
                        pre={form.pre}
                        onSetPre={(v) => update({ pre: v })}
                        post={form.post}
                        onSetPost={(v) => update({ post: v })}
                        tasks={form.tasks}
                        onSetTasks={(tasks) => update({ tasks })}
                        onSwitchToYaml={handleSwitchToYaml}
                        onBack={() => update({ step: "complex-select" })}
                        onSubmit={handleSubmit}
                    />
                );
        }
    }
}
