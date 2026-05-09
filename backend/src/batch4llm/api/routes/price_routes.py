from fastapi import APIRouter, HTTPException

from batch4llm.api.models.price_calculation_models import PriceCalculationRequest
from batch4llm.service.jwt_authenticator import JWTAuthenticator
from batch4llm.service.price_service import PriceService


def build_price_router(
    price_service: PriceService, jwt_authenticator: JWTAuthenticator
):
    router = APIRouter(prefix="/price", tags=["Price"])

    @router.post("/calculate", response_model=float)
    def calculate(request: PriceCalculationRequest):
        try:
            return price_service.estimate_batch_costs_in_usd(
                provider=request.provider,
                model=request.model,
                file_reader=request.file_reader,
                files=request.file_ids,
                prompt=request.prompt,
                output=request.output,
            )
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=str(e),
            )

    return router
