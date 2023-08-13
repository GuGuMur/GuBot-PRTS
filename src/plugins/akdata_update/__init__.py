from nonebot import on_command
from mwbot import arktool
from pathlib import Path
import subprocess

com = on_command("git update")

@com.handle()
async def _():
    # arkGH = str(Path(arktool.GameDataPosition).parent.parent)
    command = f"cd /home/bot/ArknightsGameData && git pull"
    # commandresult=subprocess.run(f"cd  && git pull", capture_output=True, text=True)
    # commandresult=subprocess.run(f"deactivate && git --work-tree={arkGH} pull && source /home/bot/qb/.venv/bin/activate", capture_output=True, text=True)
    # commandresult=os.system(command, capture_output=True, text=True)
    commandresult = subprocess.check_output(command, shell=True, universal_newlines=True)
    await com.send(f"Github拉取成功\n{commandresult}")