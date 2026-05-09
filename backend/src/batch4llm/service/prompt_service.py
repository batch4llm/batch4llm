from ..manager.database import Database
from batch4llm.manager.prompt_interpreter import prompt_interpreter


class PromptService:
    def __init__(self, db: Database):
        self.db = db

    def add(self, name: str, content: str, multi_prompt: bool, user_id: int) -> dict:
        if multi_prompt and not prompt_interpreter.check_prompt(content):
            raise ValueError("The multi prompt is not valid!")
        return self.db.prompts.add(
            name=name, content=content, multi_prompt=multi_prompt, user_id=user_id
        )

    def list(self, user_id: int) -> list[dict]:
        return self.db.prompts.list(user_id)

    def delete(self, prompt_id: int, user_id: int) -> dict:
        return self.db.prompts.delete(prompt_id=prompt_id, user_id=user_id)
