from nonebot import require, on_shell_command
from nonebot.params import Depends, ShellCommandArgs
from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message

require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from argparse import Namespace
import traceback
from .main import main
from ...models import SendMessage
from .utils import cleantext

parser = ArgumentParser(
    description=cleantext(
        """限时寻访处理Bot
    回复限时寻访 卡池名字 (--limit) """
    ),
    add_help=False,
)
parser.add_argument("gachaname", type=str)
parser.add_argument("-i", "--id", dest="id")
parser.add_argument("-h", "--help", dest="help", action="store_true")
parser.add_argument("-l", "--limit", dest="limit", action="store_true")
specialgacha = on_shell_command("限时寻访", parser=parser)


@specialgacha.handle()
async def _(
    event: GroupMessageEvent,
    session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    if args.help:
        await specialgacha.finish(parser.description)
    msgid = int(args.id)
    gachaname = args.gachaname
    limit = args.limit

    async with session.begin():
        result = await session.execute(
            select(SendMessage).where(SendMessage.msgid == msgid)
        )
        first: SendMessage = result.scalars().first()
        await main(id=first.cid, gacha_name=gachaname, limit=limit)
        await specialgacha.finish(
            Message(f"[CQ:reply,id={event.message_id}]已完成限时寻访的编辑!")
        )
        # except Exception as e:
        #     await specialgacha.finish(
        #         Message(
        #             f"[CQ:reply,id={event.message_id}]发现报错！\n{traceback.format_exc()}"
        #         )
            # )
