import { PROVIDERS } from "../config/providers";
import customLogo from "../assets/providers/custom.png";

const LOGO_MAP: Record<string, string> = Object.fromEntries(
    PROVIDERS.map(p => [p.provider, p.image as string])
);

export function logoFor(provider: string): string {
    return LOGO_MAP[provider.toLowerCase()] ?? customLogo;
}
