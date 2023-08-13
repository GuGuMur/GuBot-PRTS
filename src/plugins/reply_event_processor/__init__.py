from nonebot.matcher import Matcher
from nonebot.message import event_preprocessor
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.adapters.onebot.v11.utils import unescape
from .utils import check_reply_cq_code

@event_preprocessor
async def handle(event: MessageEvent):
    msg = unescape(str(event.dict()['raw_message']))
    try:
        msg = check_reply_cq_code(msg)
        # print(msg)
        if msg != False: # 此时msg=(msg_id,msg_without_CQcode)
            event.message[0].data["text"] = f"{msg[1]} --id {msg[0]}"
    except:
        return