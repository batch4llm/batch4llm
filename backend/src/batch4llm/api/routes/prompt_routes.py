from fastapi import APIRouter, HTTPException, Security
from starlette import status

from batch4llm.api.models.prompt_models import PromptData, PromptRequest
from batch4llm.core.exceptions import NameAlreadyExistsError
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from batch4llm.service.prompt_service import PromptService


def build_prompt_router(
    prompt_service: PromptService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/prompts", tags=["Prompts"])

    @router.post("/add")
    def add_prompt(prompt: PromptRequest, user=Security(jwt_authenticator)):
        try:
            return prompt_service.add(
                name=prompt.name,
                content=prompt.content,
                multi_prompt=prompt.multi_prompt,
                user_id=user["id"],
            )
        except NameAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    @router.get("/", response_model=list[PromptData])
    def list_prompts(archived: bool | None = None, user=Security(jwt_authenticator)):
        return prompt_service.list(user["id"], archived)

    @router.patch("/{prompt_id}/archive", response_model=PromptData)
    def archive_prompt(prompt_id: int, user=Security(jwt_authenticator)):
        try:
            return prompt_service.archive(prompt_id, user["id"])
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @router.delete("/delete/{prompt_id}")
    def delete_prompt(prompt_id: int, user=Security(jwt_authenticator)):
        try:
            return prompt_service.delete(prompt_id=prompt_id, user_id=user["id"])
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    return router
