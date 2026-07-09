from ..manager.database import Database
from batch4llm.manager.prompt_interpreter import prompt_interpreter


class PromptService:
    def __init__(self, db: Database):
        self.db = db

    def _with_step_count(self, prompt: dict) -> dict:
        step_count = None
        if prompt["multi_prompt"]:
            try:
                step_count = len(prompt_interpreter.interpret_prompt(prompt["content"]))
            except ValueError:
                step_count = None
        return {**prompt, "step_count": step_count}

    def add(self, name: str, content: str, multi_prompt: bool, user_id: int) -> dict:
        if multi_prompt and not prompt_interpreter.check_prompt(content):
            raise ValueError("The multi prompt is not valid!")
        prompt = self.db.prompts.add(
            name=name, content=content, multi_prompt=multi_prompt, user_id=user_id
        )
        return self._with_step_count(prompt)

    def list(self, user_id: int, archived: bool | None = None) -> list[dict]:
        prompts = self.db.prompts.list(user_id, archived)
        return [self._with_step_count(p) for p in prompts]

    def set_archived(self, prompt_id: int, user_id: int, archived: bool) -> dict:
        prompt = self.db.prompts.set_archived(prompt_id, user_id, archived)
        return self._with_step_count(prompt)

    def delete(self, prompt_id: int, user_id: int) -> dict:
        return self.db.prompts.delete(prompt_id=prompt_id, user_id=user_id)
