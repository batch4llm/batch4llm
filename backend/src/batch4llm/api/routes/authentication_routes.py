from fastapi import APIRouter, Response, HTTPException, Security
from batch4llm.service.login_service import LoginService
from ..models.login_models import LoginRequest, RegisterRequest
from batch4llm.service.jwt_authenticator import JWTAuthenticator


def build_authentication_router(
    login_service: LoginService,
    jwt_authenticator: JWTAuthenticator,
):
    router = APIRouter(prefix="/authentication", tags=["Authentication"])

    @router.post("/login", response_model=dict)
    def login(request: LoginRequest, response: Response):

        if not login_service.verify_password(request.username, request.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = login_service.create_access_token(request.username)

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            samesite="lax",
            secure=jwt_authenticator.secure_cookies,
        )

        return {"success": True}

    @router.post("/register", response_model=dict)
    def register(request: RegisterRequest):
        try:
            success = login_service.register_user(request.username, request.password)
            return {"success": success}
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.get("/me", response_model=dict)
    def me(user=Security(jwt_authenticator)):
        return {"success": True, "username": user["username"]}

    @router.post("/logout", response_model=dict)
    def logout(response: Response):
        response.delete_cookie(key="access_token")
        return {"success": True}

    return router
