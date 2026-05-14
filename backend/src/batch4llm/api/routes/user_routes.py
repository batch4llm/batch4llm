from fastapi import APIRouter, HTTPException, Security
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from batch4llm.service.user_service import UserService


def build_user_router(
    user_service: UserService,
    jwt_authenticator: JWTAuthenticator,
):
    router = APIRouter(prefix="/user", tags=["User"])

    @router.get("/me", response_model=dict)
    def get_me(user=Security(jwt_authenticator)):
        return user

    @router.get("/group", response_model=dict)
    def get_my_group(user=Security(jwt_authenticator)):
        group_id = user.get("group_id")
        if group_id is None:
            raise HTTPException(
                status_code=404, detail="User is not assigned to a group"
            )
        group = user_service.get_user_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        return group

    return router
