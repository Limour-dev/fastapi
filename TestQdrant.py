import httpx, json


def post_json(url: str, data: dict, headers: dict, decoding='utf-8'):
    headers.update({'Content-Type': 'application/json'})
    response = httpx.post(url, headers=headers, json=data)
    res_text = response.content.decode(encoding=decoding, errors='ignore')
    print(res_text)
    return response


test1 = post_json(
    'https://fastapi.limour.top/qdrant/hello',
    {
        'input': 'test'
    },
    {'Limour': '123456'}
)

test2 = post_json(
    'https://fastapi.limour.top/qdrant/v1',
    {
        'input': '机器人限拥令是什么'
    },
    {'Limour': '123456'}
)