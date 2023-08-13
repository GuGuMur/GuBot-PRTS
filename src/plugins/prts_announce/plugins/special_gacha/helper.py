# import asyncio
import ujson as ujson
from httpx import AsyncClient
import re

# from PIL import Image
from mwbot import Bot
from pathlib import Path
from urllib.parse import urlparse, parse_qs


async def down_pic(link: str, name: str, dir: str = "") -> str:
    if dir:
        dir = Path(dir)
    else:
        dir = Path(__file__).parent
    async with AsyncClient() as client:
        pic = await client.get(link)
        pic = pic.content
    path = str(dir / name)
    with open(path, "wb") as f:
        f.write(pic)
    return path


async def get_announce_gacha_id(link: str):
    async with AsyncClient() as client:
        res = await client.get(link)
        res = res.json()["data"]
        # print(res)
    gacha_id = parse_qs(urlparse(res["jumpLink"]).query)["param1"][0]

    pic_link = res["bannerImageUrl"]

    pic_down_link = res["bannerImageUrl"]

    if not re.search(r"\.(jpg|jpeg|png|gif)$", pic_link, re.I):
        pic_down_link += ".jpg"

    pic_suffix = pic_down_link.split(".")[-1]
    
    return {
        "gacha_id": gacha_id,
        "pic_link": pic_down_link,
        "pic_suffix": pic_suffix,
        # "filepath" : filepath
    }
