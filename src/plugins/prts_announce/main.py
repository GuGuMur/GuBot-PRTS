from nonebot import require, get_bot
from nonebot.adapters.onebot.v11 import MessageSegment

scheduler = require("nonebot_plugin_apscheduler").scheduler
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import capture_element, template_to_pic

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from nonebot_plugin_datastore.db import create_session, post_db_init
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from httpx import AsyncClient
from pathlib import Path
from random import randint

# from .config import Config
from .models import ArkAnnounce, SendMessage


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
    for k, v in model.__dict__.items():
        if k != '_sa_instance_state':
            dictionary[k] = v
    return dictionary


async def return_single_announce(id: str) -> dict:
    async with AsyncClient() as client:
        raw_data = await client.get(
            f"https://ak-webview.hypergryph.com/api/game/bulletin/{id}"
        )
        # raw_data =
        return raw_data.json()["data"]


@scheduler.scheduled_job("cron", minute="*/1", id="arkannounce")
async def _():
    # print("sched")
    async with AsyncClient() as client:
        new_info = await client.get(
            "https://ak-webview.hypergryph.com/api/game/bulletinList?target=IOS"
        )
        new_info = new_info.json()["data"]["list"]

    async with create_session() as session:
        old_info = await session.execute(select(ArkAnnounce))
        old_info = old_info.scalars().all()
        old_info = [to_dict(data) for data in old_info]
        # 列表差集操作，返回new_info的新内容
        # diff = list(set(new_info) - set(old_info))
        diff = get_difference(old_info, new_info)
        # return
        if diff:
            for i in diff:
                detail = await return_single_announce(id=i["cid"])

                rc = ArkAnnounce(**i)
                session.add(rc)
                await session.commit()
                await session.refresh(rc)
                text = f'明日方舟游戏内公告更新！\nid: {i["cid"]}\nURL:  https://ak-webview.hypergryph.com/api/game/bulletin/{i["cid"]}\ntitle: {i["title"]}'
                pics = []
                template_path = str(Path(__file__).parent / "templates")
                if detail["bannerImageUrl"]:
                    pics.append(MessageSegment.image(detail["bannerImageUrl"]))
                if detail["content"]:
                    pic_data = await template_to_pic(
                        template_path=template_path,
                        template_name="arkannounce.html",
                        templates={
                            "bannerImageUrl": detail["bannerImageUrl"],
                            "announce_title": detail["header"],
                            "content": detail["content"],
                        },
                        pages={
                            "viewport": {"width": 400, "height": 100},
                            "base_url": f"file://{template_path}",
                            "device_scale_factor":4.0,
                        },
                        
                    )
                    with open("test.png","wb") as f:
                        f.write(pic_data)
                    if pic_data:
                        pics.append(MessageSegment.image(pic_data))
                    else:
                        pics.append(MessageSegment.text("制图失败。"))
                send_msg = MessageSegment.text(text)
                for pic_cell in pics:
                    send_msg += pic_cell
                send = await get_bot().send_group_msg(
                    group_id=group, message=send_msg
                )
                try:
                    sended = SendMessage(
                        msgid=send["message_id"],
                        **i,
                        header=detail["header"],
                        content=detail["content"],
                        bannerImageUrl=detail["bannerImageUrl"],
                    )
                except Exception as e:
                    sended = SendMessage(
                        msgid=randint(1, 100000),
                        **i,
                        header=detail["header"],
                        content=detail["content"],
                        bannerImageUrl=detail["bannerImageUrl"],
                    )
                session.add(sended)
                await session.commit()
                await session.refresh(sended)
