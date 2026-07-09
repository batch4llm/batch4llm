export function fmtCost(v: number | null | undefined): string {
    if (v == null) return "—";
    if (v < 0.01) return v.toFixed(4).replace(/\.?0+$/, "");
    if (v < 1) return v.toFixed(3).replace(/\.?0+$/, "");
    return v.toFixed(2);
}
