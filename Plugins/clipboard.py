import os
from fastapi import APIRouter, Response, Header, HTTPException
from typing_extensions import Annotated
from pydantic import BaseModel


class CommonHeaders(BaseModel):
    Limour: str


class CommonBody(BaseModel):
    input: str


router = APIRouter(
    prefix="/clipboard"
)

FASTAPI_KEY = os.getenv('FASTAPI_KEY', '123456')


def isValidAuthorization(headers, response):
    response.headers["access-control-allow-headers"] = "Origin, Authorization, Limour"
    response.headers["access-control-allow-methods"] = "GET,HEAD,OPTIONS,POST"
    response.headers["access-control-allow-origin"] = "*"
    if not headers.Limour.strip().endswith(FASTAPI_KEY):
        raise HTTPException(status_code=401, detail={
            "Authorization": headers.Limour,
            'detail': "Authorization 校验失败"
        })


cb_c = ''

@router.post("/paste")
def read_root(headers: Annotated[CommonHeaders, Header()], body: CommonBody, response: Response):
    isValidAuthorization(headers, response)
    global cb_c
    cb_c = body.input
    res = {
        "Authorization": headers.Limour,
        "hash": hash(cb_c)
    }
    return res


@router.get("/copy")
async def app_qdrant(headers: Annotated[CommonHeaders, Header()], response: Response):
    isValidAuthorization(headers, response)
    res = {
        "Authorization": headers.Limour,
        "input": cb_c
    }
    return res


@router.get("/hash")
async def app_qdrant(headers: Annotated[CommonHeaders, Header()], response: Response):
    isValidAuthorization(headers, response)
    res = {
        "hash": hash(cb_c)
    }
    return res


def callback(app: APIRouter):
    app.include_router(router)
