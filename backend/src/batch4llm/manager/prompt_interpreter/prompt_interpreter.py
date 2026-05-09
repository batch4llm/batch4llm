import json
from dataclasses import dataclass


@dataclass
class MultiPrompt:
    marker: str
    prompt: str


def interpret_prompt(prompt: str) -> list[MultiPrompt]:
    try:
        data = json.loads(prompt)

        result = []

        multi_prompt = data.get("multi_prompt_v1", {})
        if not multi_prompt:
            raise ValueError("The prompt format is not recognized")

        pre = multi_prompt.get("pre", "")
        post = multi_prompt.get("post", "")

        tasks = multi_prompt.get("tasks", [])
        if len(tasks) == 0:
            raise ValueError("At least one task is required!")

        for task in tasks:
            task_prompt = task.get("prompt", "")
            task_id = task.get("id", "")

            full_prompt = f"{pre}\n{task_prompt}\n{post}".strip()
            result.append(MultiPrompt(task_id, full_prompt))

        return result

    except json.JSONDecodeError:
        raise ValueError("The prompt format is not json")


def check_prompt(prompt: str) -> bool:
    return len(interpret_prompt(prompt)) > 0
