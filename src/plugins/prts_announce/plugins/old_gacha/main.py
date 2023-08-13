from mwbot.utils import templates_env
from mwbot import arktool
# from httpx import AsyncClient
from mwbot import Bot

# from datetime import datetimef
import time
import os
from pathlib import Path

# from ..utils import get_announce_gacha_id
from .helper import get_latest_gacha, get_announce_gacha_id

# arktool.GameDataPosition = "E:/ArknightsGameData/zh_CN/gamedata"
Char = arktool.char()


# async def shop() -> dict:
#     async with AsyncClient() as client:
#         shop = await client.get("https://weedy.baka.icu/shop/high")
#         shop = shop.json()["goodList"]

#     return [
#             Char.get_char_name(shop[2]["item"]["id"]),
#             Char.get_char_name(shop[3]["item"]["id"]),
#         ]


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
        "end": "",
        "summary": "",
        "6xshop": "",
        "6x": "",
        "5xs": [],
    }
    gacha_file = return_gacha_file(id=id)
    result["name"] = gacha_file["gachaPoolName"]
    result["start"] = timestamp2time(gacha_file["openTime"])
    result["end"] = timestamp2time(gacha_file["endTime"])
    result["summary"] = gacha_file["gachaPoolSummary"]
    result["6xshop"] = Char.get_char_name(gacha_file["dynMeta"]["main6RarityCharId"])
    result["6x"] = Char.get_char_name(gacha_file["dynMeta"]["sub6RarityCharId"])
    result["5xs"] = [
        Char.get_char_name(i) for i in gacha_file["dynMeta"]["rare5CharList"]
    ]
    return result


async def main(id: str):
    link = f"https://ak-webview.hypergryph.com/api/game/bulletin/{id}"
    # print(shop_data)
    announce_info = await get_announce_gacha_id(link=link)
    gacha_id = announce_info["gacha_id"]
    wikiID = await get_latest_gacha() + 1
    gacha_data = await gacha(gacha_id)

    shop_data = [gacha_data["6xshop"], gacha_data["5xs"][0]]
    all_chars_list = [gacha_data["6xshop"], gacha_data["6x"]] + gacha_data["5xs"]

    TEMPLATES = templates_env(
        DIR_PATH=str(Path(__file__).parent / "templates"),
        variable_start_string="{$",
        variable_end_string="$}",
    )

    wiki_gacha_file_dict = {
        "id": str(wikiID).zfill(2),
        "type": "中坚寻访",
        "middle_type_cat": "常驻中坚寻访",
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "all_chars": all_chars_list,
        "stores_chars": shop_data,
    }
    gacha_wiki = TEMPLATES.render(
        T_NAME="old_gacha_file.jinja2", **wiki_gacha_file_dict
    )
    # print(gacha_wiki)

    wikitable_dict = {
        "id": str(wikiID).zfill(2),
        "pic_name": announce_info["pic_name"],
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "six_char_shop": gacha_data["6xshop"],
        "six_char": gacha_data["6x"],
        "five_char_shop": gacha_data["5xs"][0],
        "five_char_1": gacha_data["5xs"][1],
        "five_char_2": gacha_data["5xs"][2],
    }
    table_wiki = TEMPLATES.render(T_NAME="old_gacha_wikitable.jinja2", **wikitable_dict)
    # print(table_wiki)

    single_page_dict = {
        "pic_name": announce_info["pic_name"],
        "six_chars": [gacha_data["6xshop"], gacha_data["6x"]],
        "five_chars": gacha_data["5xs"],
    }
    single_page_wiki = TEMPLATES.render(
        T_NAME="old_gacha_page.jinja2", **single_page_dict
    )
    # print(single_page_wiki)
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
        "<!-- Bot Edit Anchor CLASSIC -->",
        f"""<!-- Bot Edit Anchor CLASSIC -->\n{table_wiki}""",
    )
    # print(text1)
    await bot.edit_page(title="卡池一览",text=text1,summary=f"Bot Edit CLASSIC:{str(wikiID).zfill(2)}")

    # FOR 文件：
    await bot.upload_local(filepath=announce_info["pic_filepath"],text=gacha_wiki,comment="//Upload by bot.")
    #删除文件 
    os.remove(announce_info["pic_filepath"])

    # FOR 对应的寻访页面
    await bot.edit_page(title=f"寻访模拟/中坚干员轮换卡池{str(wikiID).zfill(2)}",text=single_page_wiki,summary="//Edit by bot.")


# if __name__ == "__main__":
#     # asyncio.get_event_loop().run_until_complete(main())
#     asyncio.run(main(id="5715"))
