/** Strips a leading "models/" prefix for display only — the raw model_name is still sent to the API. */
export function displayModelName(modelName: string): string {
    return modelName.startsWith("models/") ? modelName.slice("models/".length) : modelName;
}
