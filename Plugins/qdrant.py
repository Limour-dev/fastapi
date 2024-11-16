import os
from fastapi import APIRouter, Response, Header, HTTPException
from typing_extensions import Annotated
from pydantic import BaseModel
import httpx, json


class CommonHeaders(BaseModel):
    Authorization: str


class CommonBody(BaseModel):
    input: str


router = APIRouter(
    prefix="/qdrant"
)


def isValidAuthorization(headers, response):
    response.headers["access-control-allow-headers"] = "Origin, Authorization"
    response.headers["access-control-allow-methods"] = "GET,HEAD,OPTIONS,POST"
    response.headers["access-control-allow-origin"] = "*"
    if not headers.Authorization.strip().endswith('123456'):
        raise HTTPException(status_code=401, detail={
            "Authorization": headers.Authorization,
            'detail': "Authorization 校验失败"
        })


@router.post("/hello")
def read_root(headers: Annotated[CommonHeaders, Header()], body: CommonBody, response: Response):
    isValidAuthorization(headers, response)
    res = {
        "QDRANT_RERANK_URL": QDRANT_RERANK_URL,
        "Authorization": headers.Authorization,
        "input": body.input
    }
    return res


@router.post("/v1")
def app_qdrant(headers: Annotated[CommonHeaders, Header()], body: CommonBody, response: Response):
    isValidAuthorization(headers, response)
    vector = embd([body.input])[0][1]
    res = qdrant(vector[:256])
    return (x[0] for x in rerank(res, body.input))


def callback(app: APIRouter):
    app.include_router(router)


QDRANT_EMBD_URL = os.getenv('QDRANT_EMBD_URL', 'http://localhost:8080/v1/embeddings')
QDRANT_EMBD_KEY = 'Bearer ' + os.getenv('QDRANT_EMBD_KEY', 'no-key')
QDRANT_EMBD_MODEL = os.getenv('QDRANT_EMBD_MODEL', 'text-embedding-3-small')

# 推荐硅基流动 https://siliconflow.cn
QDRANT_RERANK_URL = os.getenv('QDRANT_RERANK_URL', 'http://localhost:8081/v1/rerank')
QDRANT_RERANK_KEY = 'Bearer ' + os.getenv('QDRANT_RERANK_KEY', QDRANT_EMBD_KEY)
QDRANT_RERANK_MODEL = os.getenv('QDRANT_RERANK_MODEL', 'BAAI/bge-reranker-v2-m3')

QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333') + '/collections/%s/points/search'
QDRANT_KEY = os.getenv('QDRANT_KEY', '')


def post_json(url: str, data: dict, headers: dict, decoding='utf-8'):
    headers.update({'Content-Type': 'application/json'})
    response = httpx.post(url, headers=headers, json=data)
    res_text = response.content.decode(encoding=decoding, errors='ignore')
    try:
        res = json.loads(res_text)
    except json.decoder.JSONDecodeError as e:
        res = {}
    if response.status_code != httpx.codes.OK or not res:
        raise HTTPException(status_code=response.status_code, detail={
            "url": url,
            "data": data,
            "detail": "post_json 请求失败",
            "output": res_text
        })

    return res


def getData(r_: dict, key_: str):
    data = r_.get(key_)
    if not data:
        raise HTTPException(status_code=404, detail={
            'detail': "getData 解析失败",
            "output": r_,
            "key_": key_
        })
    return data


def embd(input_: list):
    response: dict = post_json(url=QDRANT_EMBD_URL,
                               data={
                                   'model': QDRANT_EMBD_MODEL,
                                   "encoding_format": "float",
                                   'input': input_
                               },
                               headers={'Authorization': QDRANT_EMBD_KEY})
    data: list = getData(response, 'data')
    if len(data) != len(input_):
        raise HTTPException(status_code=404, detail={
            'detail': "embd 解析长度不等",
            'input': input_,
            "output": data
        })
    return [(input_[i], data[i]['embedding']) for i in range(len(data))]


def rerank(documents_: list, query_: str, top_n_: int = 3):
    response: dict = post_json(url=QDRANT_RERANK_URL,
                               data={
                                   'model': QDRANT_RERANK_MODEL,
                                   "top_n": top_n_,
                                   'documents': documents_,
                                   "query": query_
                               },
                               headers={'Authorization': QDRANT_RERANK_KEY})
    data: list = getData(response, 'results')
    res = []
    for chunk in data:
        res.append((documents_[chunk['index']], chunk['relevance_score']))
    res.sort(key=lambda x: x[1], reverse=True)
    return res


def qdrant(vector_: list, collection_name_: str = 'my_collection', limit_: int = 5):
    response: dict = post_json(url=QDRANT_URL % collection_name_,
                               data={
                                   'vector': vector_,
                                   "limit": limit_,
                                   'with_payload': True
                               },
                               headers={'api-key': QDRANT_KEY})
    data: list = getData(response, 'result')
    return [res['payload']['text'] for res in data]
