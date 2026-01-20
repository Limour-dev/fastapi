from fastapi import APIRouter, HTTPException, Response, Request
import httpx, re

router = APIRouter(
    prefix="/subconverter"
)


@router.get("/hello")
def read_root():
    return {"Hello": "Subconverter"}


def callback(app: APIRouter):
    app.include_router(router)

# import base64
# def b64decode_maybe(s: str) -> str:
#     s2 = s.strip()
#     s2 += "=" * (-len(s2) % 4)
#     try:
#         return base64.b64decode(s2).decode("utf-8", errors="ignore")
#     except Exception:
#         return s

reg_p = re.compile(r'^proxies\s*:', re.MULTILINE)
reg_e = re.compile(r'^[^ \n\r]', re.MULTILINE)

@router.get("/clash/{url_path:path}")
async def clash(request: Request, url_path: str):
    original_query = request.url.query
    if original_query:
        url = f"https://{url_path}?{original_query}"
    else:
        url = f"https://{url_path}"

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(
                str(url),
                headers={
                    "user-agent": "clash-verge/v2.4.3"
                }
            )
            resp.raise_for_status()
    except httpx.HTTPError as e:
        # 下游网站访问失败时返回 502
        raise HTTPException(status_code=502, detail=f"Error fetching url: {e}")

    text = resp.text
    yml = text
    yml = reg_p.split(yml, maxsplit = 1)[-1]
    yml = reg_e.split(yml, maxsplit = 1)[0]
    if yml.strip():
        yml = 'proxies:' + yml
    else:
        yml = text

    return Response(
        content=yml,
        media_type="text/plain; charset=utf-8"
    )