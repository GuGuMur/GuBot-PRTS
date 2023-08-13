import asyncio, re, mwparserfromhell, subprocess
from httpx import AsyncClient
from mwbot import arktool, utils, Bot
from jinja2 import Environment
from loguru import logger
from pathlib import Path
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

# arktool.GameDataPosition = "E:/ArknightsGameData/zh_CN/gamedata"
arkGH = str(Path(arktool.GameDataPosition).parent.parent)
# character_table = arktool.read_ark_file("excel/character_table.json")
char = arktool.char()
skill_table = arktool.read_ark_file("excel/skill_table.json")
env = Environment(variable_start_string="{$", variable_end_string="$}")
TEMPLATES = utils.templates_env(
    DIR_PATH=str(Path(__file__).parent / "templates"),
    variable_start_string="{$",
    variable_end_string="$}",
)
new_tiles_table = {}

async def read_static_file(name:str):
    domains = ["https://raw.kgithub.com/","https://ghproxy.com/https://raw.githubusercontent.com/","https://fastly.jsdelivr.net/gh/","https://cdn.staticaly.com/gh/","https://ghproxy.net/https://raw.githubusercontent.com/","https://gcore.jsdelivr.net/gh/","https://jsdelivr.b-cdn.net/gh/"]
    
    async with AsyncClient() as client:
        for i in domains:
            try:
                res = await client.get(f"{i}GuGuMur/GuBot-PRTS-static/main/{name}")
                return res.json()
            except: pass


def clean_list_and_return_str(li: list) -> str:
    return "\n".join(map(str, list(set(li))))

def clean_text(text:str):
    lines = text.strip().split('\n')
    cleaned_lines = [line.strip() for line in lines if line ]
    result = '\n'.join(cleaned_lines)
    return result

def return_skill_name(skillId:str):
    return skill_table[skillId]["levels"][0]["name"]

def cell_deal_token(data:dict,title:str):
    charinfo = char.character_table[data["inst"]["characterKey"]]
    result = {}
    result["name"] = char.get_char_name(data["inst"]["characterKey"])
    if data["inst"]["level"]: result["level"] = data["inst"]["level"] 
    if data.get("initialCnt") : result["initialCnt"] = data["initialCnt"] 
    if data.get("skillIndex") != None and data["skillIndex"]!=-1: 
        charskillid_local = charinfo["skills"][data["skillIndex"]]["skillId"]
        result["skill"] = return_skill_name(charskillid_local)
    if data.get("mainSkillLvl") : result["skillLevel"] = data["mainSkillLvl"] 
    return TEMPLATES.render(T_NAME="trapper.jinja2",**result)

def deal_token(stageinfo:dict,title:str)->str:
    # print(title)
    traptext = []
    mainparams=["predefines", "hardPredefines"]
    subparams=["tokenInsts","tokenCards"]
    def return_dict_if_exist(key,dic):
        if key in dic:
            return dic[key]
        else: return False
    for maintitle in mainparams:
        if subdict:=return_dict_if_exist(maintitle,stageinfo):
            for subtitle in subparams:
                if nextdict:=return_dict_if_exist(subtitle,subdict):
                    for t in nextdict:
                        traptext.append(f"{cell_deal_token(data=t,title=title)}")

            # for k,v in stageinfo[maintitle].items(): 
            #     #k=["characterInsts","tokenInsts","characterCards","tokenCards"]
            #     if v:
            #         for t in v:
    if traptext:
        traptext = "== 未分类装置 ==\n" + "\n".join(list(set(traptext)))
        return clean_text(traptext)
    else: return ""

def deal_tiles(stageinfo:dict,title:str):
    text_list = []
    for i in stageinfo["mapData"]["tiles"]:
        #处理新tiles
        if i["tileKey"] in new_tiles_table:
            new_tiles_table[i["tileKey"]].append(title)
        else: new_tiles_table[i["tileKey"]] = [title]
        if (i["tileKey"] not in unwritetiles):
            #选择tile的处理方式
            if i["tileKey"] in tilesformat:
                template = env.from_string(tilesformat[i["tileKey"]])
                if i["blackboard"]:
                    data = {deal_key(cell["key"]): cell["value"] for cell in i["blackboard"]}
                else: data = {}
                text = template.render(**data)
                text_list.append(text)
            # else: 
            #     continue
            else: 
                logger.warning(f"{i['tileKey']} NOT FOUND USAGE!")
                if i["tileKey"] in new_tiles_table:
                    new_tiles_table[i["tileKey"]].append(title)
                else: new_tiles_table[i["tileKey"]] = [title]
                continue
    if text_list:
        tiletext = clean_list_and_return_str(text_list)
        return tiletext
    else: return ""

def shorten_stage(name:str)->str:
    if len(name.split(" ", 1)) == 2:
        namelist = name.split(" ", 1)
    else: return f"[[{name}]]"

    if re.match(r"^([\u4E00-\u9FFF]|ISW-|LT-)",name):
        # return f"[[{name}|{namelist[1]}]]"
        return f"[[{namelist[1]}]]"
    else:
        # return f"[[{name}|{namelist[0]}]]"
        return f"[[{namelist[0]}]]"

deal_key = lambda key: key.replace('[', '__').replace(']', '__').replace('.', '__')

async def deal_stage(title:str,sem:asyncio.Semaphore):
    async with sem: 
        pagetext = await bot.get_page_text(title=title)
        wikicode = pagetext[:]
        try:
            stageinfo = arktool.get_stage_info(pagetext)
        except Exception as e:
            logger.warning(f"关卡{title}出现bug！{e}")
            return 
        tiletext = deal_tiles(stageinfo=stageinfo,title=title)
        tokentext = deal_token(stageinfo=stageinfo,title=title)

        if tokentext:
            if "==作战进度奖励==" in wikicode:
                wikicode = wikicode.replace("==作战进度奖励==",f"{tokentext}\n==作战进度奖励==")
            elif "==材料掉落==" in wikicode:
                wikicode = wikicode.replace("==材料掉落==",f"{tokentext}\n==材料掉落==")
            else: 
                wikicode = wikicode.replace("==注释与链接==",f"{tokentext}\n==注释与链接==")
        else: pass
#--------------------------------------------------
        if tiletext:
            wikicode = mwparserfromhell.parse(wikicode)
            for template in wikicode.filter_templates():
                if template.name.matches("普通关卡信息") or template.name.matches("剿灭关卡信息"):
                    template.add("特殊地形效果", f"{tiletext}")
                    continue
            wikicode = str(wikicode)
        else: pass
        #FINALLY!
        if pagetext!=wikicode:
            await bot.edit_page(title=title,text=str(wikicode),summary="添加特殊地形&装置//Edit by bot.")
            # print(str(wikicode))
            ...



async def main():
    global unwritetiles, tilesformat, bot, pagelist
    unwritetiles = await read_static_file("unwritetiles.json")
    tilesformat = await read_static_file("tilesformat.json")
    bot = Bot(
        sitename="PRTS",
        api="https://prts.wiki/api.php",
        index="https://prts.wiki/index.php",
        username="GuBot",
        password="MainBot@HIDDEN",
    )
    await bot.login()
    pagelist = utils.get_all_links(content=await bot.get_page_text(title="首页/新增关卡"))
    tasks = []
    sem = asyncio.Semaphore(1) 
    
    for i in pagelist:
        task = asyncio.create_task(deal_stage(title=i,sem=sem)) 
        tasks.append(task)
    await asyncio.gather(*tasks)
    if new_tiles_table:
        newtiletext=""
        for k,v in new_tiles_table.items():
            v = [shorten_stage(name) for name in v]
            newtiletext+=f"<code>{k}</code>：{'{{dot}}'.join(list(set(v)))}\n\n"

        await bot.edit_page(title="User:GuBot/newtiles",text=newtiletext,summary="//Edit by bot.")
        # print(newtiletext)

co = on_command("关卡更新",to_me())
@co.handle()
async def _(event: GroupMessageEvent, ):
    await main()
    # if new_tiles_table:
    #     newtiletext=""
    #     for k,v in new_tiles_table.items():
    #         newtiletext+=f"<code>{k}</code>：[[{']]{{dot}}[['.join(list(set(v)))}]]\n\n"

    #     # await bot.edit_page(title="User:GuBot/newtiles",text=newtiletext,summary="//Edit by bot.")
    #     print(newtiletext)
    await co.finish(Message(f"[CQ:reply,id={event.message_id}]已完成以下关卡页面的编辑：{str(pagelist)}"))

# if __name__ == "__main__":
#     asyncio.run(main())
# 