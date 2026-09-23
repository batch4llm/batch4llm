from dataclasses import dataclass

import yaml


@dataclass
class MultiPrompt:
    marker: str
    prompt: str


def interpret_prompt(prompt: str) -> list[MultiPrompt]:
    try:
        data = yaml.safe_load(prompt)
    except yaml.YAMLError:
        raise ValueError("The prompt format is not valid yaml")

    if not isinstance(data, dict):
        raise ValueError("The prompt format is not recognized")

    result = []

    multi_prompt = data.get("multi_prompt_v1", {})
    if not multi_prompt:
        raise ValueError("The prompt format is not recognized")

    pre = multi_prompt.get("pre") or ""
    post = multi_prompt.get("post") or ""

    tasks = multi_prompt.get("tasks", [])
    if not tasks:
        raise ValueError("At least one task is required!")

    for task in tasks:
        task_prompt = task.get("prompt", "")
        task_id = task.get("id", "")

        full_prompt = f"{pre}\n{task_prompt}\n{post}".strip()
        result.append(MultiPrompt(task_id, full_prompt))

    return result


def check_prompt(prompt: str) -> bool:
    return len(interpret_prompt(prompt)) > 0
