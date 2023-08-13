from mwbot.utils import templates_env
from mwbot import arktool
from httpx import AsyncClient
from mwbot import Bot
import asyncio

import time
import os
from pathlib import Path

from .helper import get_announce_gacha_id, down_pic

# arktool.GameDataPosition = "E:/ArknightsGameData/zh_CN/gamedata"
Char = arktool.char()


def return_gacha_file(id: str):
    for i in arktool.read_ark_file("excel/gacha_table.json")["gachaPoolClient"]:
        if i["gachaPoolId"] == id:
            return i


def timestamp2time(time_stamp: int, result_format: str = "%Y-%m-%d %H:%M"):
    time_array = time.localtime(time_stamp)
    end = time.strftime(result_format, time_array)
    return end


async def gacha(id: str) -> dict:
    result = {
        "id": id,
        "name": "",
        "start": "",
        "gacha_page_start_time": "",
        "end": "",
        "summary": "",
        "six_stars":"",
        "five_stars":"",
        "all_chars":"",
    }
    gacha_file = return_gacha_file(id=id)
    result["name"] = gacha_file["gachaPoolName"]
    result["start"] = timestamp2time(gacha_file["openTime"])
    result["gacha_page_start_time"] = timestamp2time(gacha_file["openTime"],result_format="%Y%m%d")
    result["end"] = timestamp2time(gacha_file["endTime"])
    result["summary"] = gacha_file["gachaPoolSummary"]
    async with AsyncClient() as client:
        gacha = await client.get(f"https://weedy.baka.icu/gacha/{id}")
        gacha = gacha.json()
        if gacha["code"] == 0:
            gacha = gacha["detail"]["up"]
            result["six_stars"] = [Char.get_char_name(x) for x in gacha[0]["charIdList"]]
            result["five_stars"] = [Char.get_char_name(x) for x in gacha[1]["charIdList"]]
            result["all_chars"] = result["six_stars"]+result["five_stars"]
        else: 
            result["six_stars"] = []
            result["five_stars"] = []
            result["all_chars"] = []

    return result

def charlist_to_tplts(l:list)->str:
    text = ""
    for i in l:
        text += ("{{干员头像|" + i + "}}") #f"{{ xx | {i} }}""
    return text

async def main(id: str, gacha_name:str, limit:bool=False):
    link = f"https://ak-webview.hypergryph.com/api/game/bulletin/{id}"
    # print(shop_data)
    announce_info = await get_announce_gacha_id(link=link)
    gacha_id = announce_info["gacha_id"]
    gacha_data = await gacha(gacha_id)

    TEMPLATES = templates_env(
        DIR_PATH=str(Path(__file__).parent / "templates"),
        variable_start_string="{$",
        variable_end_string="$}",
    )

    wiki_gacha_file_dict = {
        "gacha_name" : gacha_name,
        "limit": limit,
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "all_chars": gacha_data["all_chars"],
    }
    gacha_wiki = TEMPLATES.render(
        T_NAME="special_gacha_file.jinja2", **wiki_gacha_file_dict
    )
    # print(gacha_wiki)

    wikitable_dict = {
        "gacha_name" : gacha_name,
        "suffix": announce_info["pic_suffix"],
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "sixstar_tplt_text": charlist_to_tplts(gacha_data["six_stars"]) ,
        "fivestar_tplt_text": charlist_to_tplts(gacha_data["five_stars"]),
    }
    table_wiki = TEMPLATES.render(T_NAME="special_gacha_wikitable.jinja2", **wikitable_dict)
    # print(table_wiki)

    single_page_dict = {
        "gacha_name" : gacha_name,
        "limit": limit,
        "suffix": announce_info["pic_suffix"],
        "starttime": gacha_data["gacha_page_start_time"],
        "six_chars": gacha_data["six_stars"],
        "five_chars": gacha_data["five_stars"]
    }
    single_page_wiki = TEMPLATES.render(
        T_NAME="special_gacha_page.jinja2", **single_page_dict
    )
    print(single_page_wiki)
    bot = Bot(
        sitename="PRTS",
        api="https://prts.wiki/api.php",
        index="https://prts.wiki/index.php",
        username="GuBot",
        password="MainBot@HIDDEN",
    )
    await bot.login()

    # FOR 卡池一
    text1 = await bot.get_page_text(title="卡池一览")
    text1 = text1.replace(
        "<!-- Bot Edit Anchor SINGLE -->",
        f"""<!-- Bot Edit Anchor SINGLE -->\n{table_wiki}""",
    )
    # print(text1)
    await bot.edit_page(title="卡池一览",text=text1,summary=f"Bot Edit SINGLE:{id}")

    text2 = await bot.get_page_text(title="卡池一览/限时寻访")
    if limit:
        text2 = text2.replace(
            "<!-- Bot Edit Anchor SINGLE_LIMIT -->",
            f"""<!-- Bot Edit Anchor SINGLE_LIMIT -->\n{table_wiki}""",
        )
    else: 
        text2 = text2.replace(
            "<!-- Bot Edit Anchor SINGLE -->",
            f"""<!-- Bot Edit Anchor SINGLE -->\n{table_wiki}""",
        )
    # print(text2)
    await bot.create_page(title="卡池一览/限时寻访",text=text2,summary=f"Bot Edit SINGLE:{id}")
    
    # FOR 文件：
    filepath = await down_pic(link=announce_info["pic_link"], name=f"{gacha_name}.{announce_info['pic_suffix']}")
    await bot.upload_local(filepath=filepath,text=gacha_wiki,comment="//Upload by bot.")
    #删除文件 
    os.remove(filepath)

    # FOR 对应的寻访页面
    await bot.edit_page(title=f"寻访模拟/{gacha_name}",text=single_page_wiki,summary="//Edit by bot.")


# if __name__ == "__main__":
# #     # asyncio.get_event_loop().run_until_complete(main())
#     asyncio.run(main(id="7639",gacha_name="沙洲引路人 复刻",limit=True))
