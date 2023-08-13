from .deal import *
from .file import *
import os
from pathlib import Path
# import asyncio

async def main(id:str, wikiname:str):
    basic = await firstDeal(id=id)
    dir = str(Path(__file__).parent / wikiname)
    try:
        os.mkdir(dir)
    except:
        pass
    info = await announceDealt(name=wikiname, text=basic["content"])
    # with open(str(Path(__file__).parent / "text.txt"), "w", encoding="utf-8") as w:
    #     w.write(info["wikitext"])
    # print(info["img"])
    pics = {}
    for k, v in info["img"].items():
        await down_pic(link=v["src"], name=k, dir=dir)
        pics[k] = dir+"/"+k
    # print({
    #     "wikitext": info["wikitext"],
    #     "pics" : pics
    # })
    return {
        "wikitext": info["wikitext"],
        "pics" : pics
    }


# if __name__ == "__main__":
    asyncio.run(main(id="5716", wikiname="夏活2023"))
