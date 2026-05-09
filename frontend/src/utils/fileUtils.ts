export function formatBytes(bytes: number): string {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1_048_576) return (bytes / 1024).toFixed(1) + " KB";
    if (bytes < 1_073_741_824) return (bytes / 1_048_576).toFixed(1) + " MB";
    return (bytes / 1_073_741_824).toFixed(2) + " GB";
}

export function formatDate(iso: string): string {
    return new Date(iso).toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric",
    });
}

export function getExt(name: string): string {
    const parts = name.split(".");
    return parts.length > 1 ? parts[parts.length - 1].toUpperCase() : "FILE";
}
