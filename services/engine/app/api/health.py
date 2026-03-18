from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, bool]:
    return {"ok": True}
