import pytest

from batch4llm.manager.prompt_interpreter.prompt_interpreter import (
    MultiPrompt,
    check_prompt,
    interpret_prompt,
)


def test_interpret_prompt_parses_yaml_tasks():
    prompt = """
multi_prompt_v1:
  pre: "pre-text"
  post: "post-text"
  tasks:
    - id: task_a
      prompt: "prompt-a"
    - id: task_b
      prompt: "prompt-b"
"""

    result = interpret_prompt(prompt)

    assert result == [
        MultiPrompt(marker="task_a", prompt="pre-text\nprompt-a\npost-text"),
        MultiPrompt(marker="task_b", prompt="pre-text\nprompt-b\npost-text"),
    ]


def test_interpret_prompt_supports_block_scalars():
    prompt = """
multi_prompt_v1:
  tasks:
    - id: task_a
      prompt: |
        line one
        line two
"""

    result = interpret_prompt(prompt)

    assert result == [MultiPrompt(marker="task_a", prompt="line one\nline two")]


def test_interpret_prompt_rejects_invalid_yaml():
    with pytest.raises(ValueError):
        interpret_prompt(":::not yaml::: [")


def test_interpret_prompt_rejects_non_mapping():
    with pytest.raises(ValueError):
        interpret_prompt("just a plain string")


def test_interpret_prompt_requires_multi_prompt_key():
    with pytest.raises(ValueError):
        interpret_prompt("some_other_key: {}")


def test_interpret_prompt_requires_at_least_one_task():
    with pytest.raises(ValueError):
        interpret_prompt("multi_prompt_v1:\n  pre: a\n")


def test_check_prompt_true_for_valid_prompt():
    prompt = "multi_prompt_v1:\n  tasks:\n    - id: a\n      prompt: x\n"

    assert check_prompt(prompt) is True


def test_check_prompt_raises_for_invalid_prompt():
    with pytest.raises(ValueError):
        check_prompt("not valid")
