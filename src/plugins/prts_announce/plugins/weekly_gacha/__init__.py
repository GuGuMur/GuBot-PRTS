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
from .utils import *

parser = ArgumentParser(
    description=cleantext(
        """周常寻访处理Bot
        方案一： 直接回复对应的消息：周常寻访
        方案二： 人眼筛一下五六星，回复指令：周常寻访/norm --six_star 六星1.六星2 --five_star 五星1.五星2.五星3 --shop 商店六星.商店五星 （注意要有空格！）
        """
    ),
    add_help=False,
)
parser.add_argument("--six_star", type=str, default="")
parser.add_argument("--five_star", type=str, default="")
parser.add_argument("--shop", type=str, default="")
parser.add_argument("-h", "--help", dest="help", action="store_true")
parser.add_argument("-i", "--id", dest="id", default="")
weeklygacha = on_shell_command("周常寻访", aliases={"norm"}, parser=parser)


@weeklygacha.handle()
async def _(
    event: GroupMessageEvent,
    session: AsyncSession = Depends(get_session),
    args: Namespace = ShellCommandArgs(),
):
    if args.help:
        await weeklygacha.finish(parser.description)
    msgid = int(args.id)
    six_star = args.six_star
    six_star_list = six_star.split(".") if six_star!="" else []
    five_star = args.five_star
    five_star_list = five_star.split(".") if five_star!="" else []
    shop = args.shop
    shop_list = shop.split(".") if shop!="" else []
    print(six_star_list, five_star_list, shop_list)
    async with session.begin():
        
        result = await session.execute(
            select(SendMessage).where(SendMessage.msgid == msgid)
        )
        first: SendMessage = result.scalars().first()
        await main(
            id=first.cid,
            shop=shop_list,
            six_star_list=six_star_list,
            five_star_list=five_star_list,
        )
        await weeklygacha.finish(
            Message(f"[CQ:reply,id={event.message_id}]已完成周常寻访的编辑!")
        )
