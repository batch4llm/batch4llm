from fastapi import APIRouter, HTTPException, Security
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from ...core.exceptions import NameAlreadyExistsError
from ...service.user_service import UserService


def build_admin_router(
    user_service: UserService,
    jwt_authenticator: JWTAuthenticator,
):
    router = APIRouter(prefix="/admin", tags=["Admin"])

    @router.post("/set_group", response_model=dict)
    def set_group(username: str, group_id: int, user=Security(jwt_authenticator)):
        if user["is_admin"]:
            try:
                return user_service.set_user_group(username, group_id)
            except Exception as e:
                raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=403, detail="Not authorized")

    @router.get("/users", response_model=list[dict])
    def get_users(user=Security(jwt_authenticator)):
        if user["is_admin"]:
            return user_service.get_users()
        raise HTTPException(status_code=403, detail="Not authorized")

    @router.get("/groups", response_model=list[dict])
    def get_groups(user=Security(jwt_authenticator)):
        if user["is_admin"]:
            return user_service.get_groups()
        raise HTTPException(status_code=403, detail="Not authorized")

    @router.get("/first", response_model=bool)
    def test_for_admin_user():
        return not user_service.does_any_user_exist()

    @router.post("/add_group", response_model=dict)
    def add_group(group_name: str, user=Security(jwt_authenticator)):
        if user["is_admin"]:
            try:
                return user_service.add_group(group_name)
            except NameAlreadyExistsError as e:
                raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=403, detail="Not authorized")

    return router
