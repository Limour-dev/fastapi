import httpx, json


def post_json(url: str, data: dict, headers: dict, decoding='utf-8'):
    headers.update({'Content-Type': 'application/json'})
    response = httpx.post(url, headers=headers, json=data)
    res_text = response.content.decode(encoding=decoding, errors='ignore')
    print(res_text)
    return response


test1 = post_json(
    'http://127.0.0.1:8000/qdrant/hello',
    {
        'input': 'test'
    },
    {'Authorization': '123456'}
)

test2 = post_json(
    'http://127.0.0.1:8000/qdrant/v1',
    {
        'input': '机器人限拥令是什么'
    },
    {'Authorization': '123456'}
)