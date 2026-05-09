import styles from "./FileTag.module.css";

const COLOR_COUNT = 8;

export function tagColorIndex(tag: string): number {
    let h = 0;
    for (let i = 0; i < tag.length; i++) h = (Math.imul(31, h) + tag.charCodeAt(i)) | 0;
    return Math.abs(h) % COLOR_COUNT;
}

type FileTagProps = {
    tag: string;
    filter?: boolean;
    active?: boolean;
    onClick?: () => void;
};

export function FileTag({ tag, filter = false, active = true, onClick }: FileTagProps) {
    const ci = tagColorIndex(tag);
    const cls = [
        styles.tag,
        styles[`tagC${ci}`],
        filter ? styles.filterTag : "",
        filter && !active ? styles.inactiveTag : "",
    ].filter(Boolean).join(" ");
    return (
        <span className={cls} onClick={onClick}>
            <span className={styles.tagDot} />
            {tag}
        </span>
    );
}
