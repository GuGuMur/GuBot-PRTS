from nonebot import require, on_shell_command
from nonebot.params import  Depends, ShellCommandArgs
from nonebot.rule import ArgumentParser
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message
require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from argparse import Namespace
from .main import main
from ...models import SendMessage

parser = ArgumentParser(description='中坚寻访处理Bot')
parser.add_argument("-i", "--id", dest="id")
rchide = on_shell_command("中坚寻访",aliases={"classic"}, parser=parser)
@rchide.handle()
async def _(event: GroupMessageEvent, 
            session: AsyncSession = Depends(get_session),
            args: Namespace = ShellCommandArgs()):
    # if args.help:
    #     await update.finish("weather plugin update")
    mid= int(args.id)
    async with session.begin():
        try:
            result = await session.execute(
                select(SendMessage).where(SendMessage.msgid == mid))
            first: SendMessage = result.scalars().first()
            await main(id=first.cid)
            await rchide.finish(Message(f"[CQ:reply,id={event.message_id}]已完成中坚寻访的编辑!"))
        except: pass #这条指令与你无关了
