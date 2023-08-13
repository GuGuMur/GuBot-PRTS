from nonebot import require,on_shell_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Bot, Message
from nonebot.params import ShellCommandArgs
from nonebot.rule import ArgumentParser
from argparse import Namespace
from nonebot.params import  Depends, ShellCommandArgs
from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from argparse import Namespace
from .main import main
from .utils import *
from ...models import SendMessage
from mwbot import Bot

parser = ArgumentParser(
    add_help=False,
    description=cleantext(
        """需要创建页面的活动公告处理
        1. 回复鸽机发送的消息
        2. 指令为：活动公告 页面名
        3. 例：活动公告 夏活2023 => 创建页面 夏活2023/活动公告，上传图片File:活动预告 夏活2023 [num].[suffix]"""
    ),
)
parser.add_argument("name", type=str, help="tags!")
parser.add_argument("--id", dest="id", default="")
parser.add_argument("-h", "--help", dest="help", action="store_true")
announcer = on_shell_command("活动公告", aliases={"hdgg"}, parser=parser)


@announcer.handle()
async def setu_handle(
    event: GroupMessageEvent,
    session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    # 处理帮助
    if args.help:
        await announcer.finish(parser.description)
    # print(str(args))
    name = args.name
    msgid = args.id

    async with session.begin():
        try:
            result = await session.execute(
                select(SendMessage).where(SendMessage.msgid == msgid))
            first: SendMessage = result.scalars().first()
            result = await main(id=first.cid, wikiname=name)
            bot = Bot(
                sitename="PRTS",
                api="https://prts.wiki/api.php",
                index="https://prts.wiki/index.php",
                username="GuBot",
                password="MainBot@HIDDEN",
            )
            await bot.login()
            await bot.edit_page(title=f"{name}/活动公告", text=result["wikitext"])
            for k, v in result["pics"].items():
                await bot.upload_local(filepath=v,servername=k, text="",comment="//Upload by bot.")
            await announcer.finish(Message(f"[CQ:reply,id={event.message_id}]已完成ID为{first.cid}的活动公告编辑!"))
        except: pass #这条指令与你无关了
