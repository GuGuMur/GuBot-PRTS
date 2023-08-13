from nonebot import require, get_bot, logger
from nonebot.adapters.onebot.v11 import MessageSegment

scheduler = require("nonebot_plugin_apscheduler").scheduler
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import capture_element

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import create_session, post_db_init
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

# from httpx import AsyncClient
from .get_rc import topic_rc

# from .config import Config
from .models import RCInfo, SendMessage
from random import randint
from .command import *

# global_config = get_driver().config
group = 114514


def get_difference(a, b):
    difference = []
    for item in b:
        if item not in a:
            difference.append(item)
    return difference


def to_dict(model):
    dictionary = {}
    for column in model.__table__.columns:
        if column.name != "_sa_instance_state":
            dictionary[column.name] = getattr(model, column.name)
    return dictionary


def clear_list(dealt):
    hash_table = []
    result = []
    for i in dealt:
        if [i["title"], i["author"]] not in hash_table:
            hash_table.append([i["title"], i["author"]])
            result.append(i)
        else:
            pass
    return result


@scheduler.scheduled_job("cron", minute="*/5", id="rc_topic_and_talk")
async def _():
    # print("sched")
    # async with AsyncClient() as client:
    #     # try:
    #     new_info = await client.get("http://49.232.175.124:8765/api/prts/rc")
    #     new_info = new_info.json()
    #     new_info = clear_list(new_info)
    #     for i in new_info:
    #         i["primary_key"]=f"{i['title']}-{i['author']}-{i['updated']}"
    #         # print("new:",new_info)
    #     # except Exception as e:
    #     #     logger.warning("PRTS RC neterror!")
    #     #     return
    new_info = await topic_rc()
    new_info = clear_list(new_info)
    for i in new_info:
        i["primary_key"] = f"{i['title']}-{i['author']}-{i['updated']}"

    async with create_session() as session:
        old_info = await session.execute(select(RCInfo))
        old_info = old_info.scalars().all()
        old_info = [to_dict(data) for data in old_info]
        # print("old:",old_info)
        # return
        # 列表差集操作，返回new_info的新内容
        # diff = list(set(new_info) - set(old_info))
        diff = get_difference(old_info, new_info)
        # return
        if diff:
            # print("diff",diff)
            for i in diff:
                # async with create_session() as session:
                rc = RCInfo(**i)
                session.add(rc)
                await session.commit()
                await session.refresh(rc)
                # async with create_session() as session:

                # try:
                text = f"{i['title']}（{i['link']}）——{i['author']}；{i['updated']}"
                element = "#bodyContent > #mw-content-text"
                pic = await capture_element(
                    f"https://prts.wiki/index.php?title={i['title']}",
                    element,
                    viewport={"width": 1000, "height": 10000},
                    device_scale_factor=1,
                    timeout=0,
                )
                if pic:
                    picmsg = MessageSegment.image(pic)
                else:
                    picmsg = "!!!服务器与PRTS连接错误，制图失败。"
                send = await get_bot().send_group_msg(
                    group_id=group, message=(text + picmsg)
                )
                sended = SendMessage(id=send["message_id"], **i)
                logger.info(f"PRTS RC PLUGIN SEND:{i}")
                # sended = SendMessage(id=randint(1,100000),link=i["link"])
                # except:
                # sended = SendMessage(id=randint(1,100000),**i)
                session.add(sended)
                await session.commit()
                await session.refresh(sended)
