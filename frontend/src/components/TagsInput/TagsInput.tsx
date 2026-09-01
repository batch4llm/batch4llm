import { useState, type KeyboardEvent } from "react";
import { FileTag } from "../FileTag/FileTag";
import styles from "./TagsInput.module.css";

type Props = {
    tags: string[];
    onChange: (tags: string[]) => void;
    placeholder?: string;
};

export function TagsInput({ tags, onChange, placeholder = "Add tag…" }: Props) {
    const [value, setValue] = useState("");

    function addTag(raw: string) {
        const t = raw.trim();
        if (!t || tags.includes(t)) return;
        onChange([...tags, t]);
    }

    function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
        if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            addTag(value);
            setValue("");
        } else if (e.key === "Backspace" && value === "" && tags.length > 0) {
            onChange(tags.slice(0, -1));
        }
    }

    function handleBlur() {
        if (value.trim()) {
            addTag(value);
            setValue("");
        }
    }

    function removeTag(tag: string) {
        onChange(tags.filter(t => t !== tag));
    }

    return (
        <div className={styles.wrapper}>
            {tags.map(t => (
                <FileTag key={t} tag={t} onRemove={() => removeTag(t)} />
            ))}
            <input
                type="text"
                className={styles.input}
                value={value}
                placeholder={tags.length === 0 ? placeholder : ""}
                onChange={e => setValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={handleBlur}
            />
        </div>
    );
}
