import yaml from "js-yaml";

export type PromptTask = {
    id: string;
    prompt: string;
};

export type MultiPromptStructured = {
    pre: string;
    post: string;
    tasks: PromptTask[];
};

export function structuredToYaml({ pre, post, tasks }: MultiPromptStructured): string {
    const doc: Record<string, unknown> = {};
    if (pre.trim()) doc.pre = pre;
    if (post.trim()) doc.post = post;
    doc.tasks = tasks.map(t => ({ id: t.id, prompt: t.prompt }));

    return yaml.dump({ multi_prompt_v1: doc }, { lineWidth: -1 });
}

// Only succeeds for YAML that maps onto the visual editor's schema exactly -
// unknown keys, non-string fields or duplicate ids fall back to the raw
// YAML editor instead of silently dropping data the visual editor can't show.
export function yamlToStructured(content: string): MultiPromptStructured | null {
    let data: unknown;
    try {
        data = yaml.load(content);
    } catch {
        return null;
    }

    if (typeof data !== "object" || data === null || Array.isArray(data)) return null;
    const root = data as Record<string, unknown>;
    if (Object.keys(root).length !== 1) return null;

    const multiPrompt = root.multi_prompt_v1;
    if (typeof multiPrompt !== "object" || multiPrompt === null || Array.isArray(multiPrompt)) return null;
    const mp = multiPrompt as Record<string, unknown>;
    if (!Object.keys(mp).every(k => k === "pre" || k === "post" || k === "tasks")) return null;

    const pre = mp.pre;
    const post = mp.post;
    if (pre !== undefined && typeof pre !== "string") return null;
    if (post !== undefined && typeof post !== "string") return null;

    if (!Array.isArray(mp.tasks) || mp.tasks.length === 0) return null;

    const tasks: PromptTask[] = [];
    for (const task of mp.tasks) {
        if (typeof task !== "object" || task === null || Array.isArray(task)) return null;
        const t = task as Record<string, unknown>;
        if (!Object.keys(t).every(k => k === "id" || k === "prompt")) return null;
        if (typeof t.id !== "string" || typeof t.prompt !== "string") return null;
        if (!t.id.trim()) return null;
        tasks.push({ id: t.id, prompt: t.prompt });
    }

    const ids = tasks.map(t => t.id);
    if (new Set(ids).size !== ids.length) return null;

    return { pre: pre ?? "", post: post ?? "", tasks };
}

// Mirrors the backend's interpret_prompt/check_prompt (prompt_interpreter.py),
// which is more lenient than yamlToStructured - it just needs multi_prompt_v1
// with at least one task, extra/unknown keys are ignored. Used to show the
// same error the user would otherwise only see after submitting.
export function validateMultiPromptContent(content: string): string | null {
    if (!content.trim()) return "The prompt is empty.";

    let data: unknown;
    try {
        data = yaml.load(content);
    } catch {
        return "The prompt format is not valid YAML.";
    }

    if (typeof data !== "object" || data === null || Array.isArray(data)) {
        return "The prompt format is not recognized.";
    }

    const multiPrompt = (data as Record<string, unknown>).multi_prompt_v1;
    if (!multiPrompt || typeof multiPrompt !== "object" || Array.isArray(multiPrompt)) {
        return "The prompt format is not recognized.";
    }

    const tasks = (multiPrompt as Record<string, unknown>).tasks;
    if (!Array.isArray(tasks) || tasks.length === 0) {
        return "At least one task is required.";
    }

    return null;
}
