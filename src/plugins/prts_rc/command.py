from nonebot import require, on_shell_command
from nonebot.params import  Depends, ShellCommandArgs
from nonebot.rule import ArgumentParser
require("nonebot_plugin_datastore")
from nonebot_plugin_datastore import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from argparse import Namespace
from .models import *


#---------------------------------------------
parser = ArgumentParser(description='PRTS RC Plugin:回复鸽机发送的RC消息/rchide, 隐藏这条Topic!')
parser.add_argument("-i", "--id", dest="id")
rchide = on_shell_command("rchide",parser=parser)
@rchide.handle()
async def _(session: AsyncSession = Depends(get_session),
            args: Namespace = ShellCommandArgs()):
    # if args.help:
    #     await update.finish("weather plugin update")
    mid= int(args.id)
    async with session.begin():
        result = await session.execute(
            select(SendMessage).where(SendMessage.id == mid))
        first: SendMessage = result.scalars().first()
        msg = f"HIDE!{first.link}"
    await rchide.finish(msg)
