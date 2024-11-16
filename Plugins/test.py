from fastapi import APIRouter

router = APIRouter(
    prefix="/test"
)


@router.get("/hello")
def read_root():
    return {"Hello": "Test"}


def callback(app: APIRouter):
    app.include_router(router)
