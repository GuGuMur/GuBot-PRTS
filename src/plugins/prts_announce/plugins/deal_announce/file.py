# from PIL import Image
from httpx import AsyncClient
from pathlib import Path
# import os

# async def file_trans(name):
#     purename = os.path.splitext(os.path.basename(name))[0]
#     image = Image.open(f"{purename}.png")
#     image=image.convert('RGB')
#     image.save(f"{purename}.jpg")


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
