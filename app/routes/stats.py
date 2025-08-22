from fastapi import APIRouter, HTTPException
from app.models.schemas import SuccessResponse
from app.services.aggregator import aggregated_tokenomics

router = APIRouter()

@router.get("/tokenomics", response_model=SuccessResponse)
async def get_tokenomics():
    try:
        data = await aggregated_tokenomics()
        return SuccessResponse(data=data, message="Market data retrieved successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))