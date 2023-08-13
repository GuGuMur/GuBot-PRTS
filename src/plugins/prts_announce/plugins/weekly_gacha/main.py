from mwbot.utils import templates_env
from mwbot import arktool
from httpx import AsyncClient
from mwbot import Bot
# import asyncio

# from datetime import datetimef
import time
import os
from pathlib import Path

# from ..utils import get_announce_gacha_id
from .helper import get_latest_gacha, get_announce_gacha_id

# arktool.GameDataPosition = "E:/ArknightsGameData/zh_CN/gamedata"
Char = arktool.char()


async def shopdata() -> dict:
    async with AsyncClient() as client:
        shop = await client.get("https://weedy.baka.icu/shop/high")
        shop = shop.json()["goodList"]

    # return {
    #     "shop_standerd": [
    #         Char.get_char_name(shop[0]["item"]["id"]),
    #         Char.get_char_name(shop[1]["item"]["id"]),
    #     ],
    #     "shop_middle": [
    #         Char.get_char_name(shop[2]["item"]["id"]),
    #         Char.get_char_name(shop[3]["item"]["id"]),
    #     ],
    # }
    return [Char.get_char_name(shop[0]["item"]["id"]),
            Char.get_char_name(shop[1]["item"]["id"]),]


def return_gacha_file(id: str):
    for i in arktool.read_ark_file("excel/gacha_table.json")["gachaPoolClient"]:
        if i["gachaPoolId"] == id:
            return i


def timestamp2time(time_stamp: int, result_format: str = "%Y-%m-%d %H:%M"):
    time_array = time.localtime(time_stamp)
    end = time.strftime(result_format, time_array)
    return end


async def gacha(id: str) -> dict:
    gacha_file = return_gacha_file(id=id)
    shop_file = await shopdata()
    result = {
        "id": id,
        "name": gacha_file["gachaPoolName"],
        "start": timestamp2time(gacha_file["openTime"]),
        "end": timestamp2time(gacha_file["endTime"]),
        "summary": gacha_file["gachaPoolSummary"],
        "six_star_shop": shop_file[0],
        "six_stars": [],
        "five_star_shop": shop_file[1],
        "five_stars": [],
    }
    try:
        async with AsyncClient() as client:
            gacha = await client.get(f"https://weedy.baka.icu/gacha/{id}")
            gacha = gacha.json()
            if gacha["code"] == 0:
                gacha = gacha["detail"]["up"]
                result["six_stars"] = [
                    Char.get_char_name(i) for i in gacha[0]["charIdList"]
                ]
                result["five_stars"] = [
                    Char.get_char_name(i) for i in gacha[1]["charIdList"]
                ]
            else:
                return result
            # gacha = gacha["detail"]
            # result["pool"] = process_last_layer(data=gacha)
        # print(result)
    except Exception as e:
        pass
    return result


async def main(
    id: str, shop: list = [], six_star_list: list = [], five_star_list: list = []
):
    link = f"https://ak-webview.hypergryph.com/api/game/bulletin/{id}"
    # print(shop_data)
    announce_info = await get_announce_gacha_id(link=link)
    gacha_id = announce_info["gacha_id"]
    wikiID = await get_latest_gacha() + 1
    gacha_data = await gacha(gacha_id)

    # shop_file = await shop()
    # shop_file = shop_file["shop_standerd"]
    if not six_star_list:
        six_star_list = gacha_data["six_stars"]
    if not five_star_list:
        five_star_list = gacha_data["five_stars"]
    if not shop:
        shop = await shopdata()
    print(shop)
    shop_data = [shop[0], shop[1]]
    all_chars_list = six_star_list + five_star_list
    six_star_norm_list = [x for x in six_star_list if x != shop[0]]
    five_star_norm_list = [x for x in five_star_list if x != shop[1]]
    TEMPLATES = templates_env(
        DIR_PATH=str(Path(__file__).parent / "templates"),
        variable_start_string="{$",
        variable_end_string="$}",
    )

    wiki_gacha_file_dict = {
        "id": str(wikiID).zfill(3),
        "type": "标准寻访",
        "standerd_type_cat": "常驻标准寻访",
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "all_chars": all_chars_list,
        "stores_chars": shop_data,
    }
    gacha_wiki = TEMPLATES.render(
        T_NAME="weekly_gacha_file.jinja2", **wiki_gacha_file_dict
    )
    # print(gacha_wiki)

    table_dict = {
        "id": str(wikiID).zfill(3),
        "pic_name": announce_info["pic_name"],
        "starttime": gacha_data["start"],
        "endtime": gacha_data["end"],
        "six_char_shop": shop_data[0],
        "six_char": six_star_norm_list[0],
        "five_char_shop": shop_data[1],
        "five_char_1": five_star_norm_list[0],
        "five_char_2": five_star_norm_list[1],
    }
    table_wiki = TEMPLATES.render(T_NAME="weekly_gacha_wikitable.jinja2", **table_dict)
    # print(table_wiki)

    single_page_dict = {"suffix": announce_info["pic_name"].split(".")[-1]}
    single_page_wiki = TEMPLATES.render(
        T_NAME="weekly_gacha_page.jinja2", **single_page_dict
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

    # with open(str(Path(__file__).parent / "TEST.txt"), "w") as f:
    #     f.write(gacha_wiki)
    #     f.write(table_wiki)
    #     f.write(single_page_wiki)
    # FOR 卡池一览
    for wikiPageTitle in ["卡池一览", "卡池一览/常驻标准寻访/2023"]:
        text1 = await bot.get_page_text(title=wikiPageTitle)
        text1 = text1.replace(
            "<!-- Bot Edit Anchor NORM -->",
            f"""<!-- Bot Edit Anchor NORM -->\n{table_wiki}""",
        )
        # print(text1)
        await bot.edit_page(title=wikiPageTitle,text=text1,summary=f"Bot Edit NORM:{str(wikiID).zfill(3)}")

    # FOR 文件：
    await bot.upload_local(filepath=announce_info["pic_filepath"],text=gacha_wiki,comment="//Upload by bot.")
    # print(gacha_wiki)
    # 删除文件
    os.remove(announce_info["pic_filepath"])

    # FOR 对应的寻访页面
    await bot.edit_page(title=f"寻访模拟/干员轮换卡池{str(wikiID).zfill(3)}",text=single_page_wiki,summary="//Edit by bot.")
    # print(single_page_wiki)


# if __name__ == "__main__":
#     # asyncio.get_event_loop().run_until_complete(main())
#     asyncio.run(
#         main(
#             id="1163",
#         )
#     )
