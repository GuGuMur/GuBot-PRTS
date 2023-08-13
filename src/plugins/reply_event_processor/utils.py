import re

cq_pattern = re.compile(r'((\[(.*?)\:(.*?)\])|(\[CQ:[^\]]+\]))')

remove_cq_code = lambda text : re.sub(cq_pattern, '', text).strip()

def find_reply_cq_code(text:str):
    reply_pattern = re.compile(r'\[((CQ:reply,id=)|(reply:id=))(?P<replyid>(-?[0-9]+))\]')
    matches = re.search(reply_pattern,text)
    if matches:
        reply_id = matches.group("replyid")
        return reply_id, remove_cq_code(text)
    else:
        return False

def check_reply_cq_code(text):
    if cq_pattern.search(text):
        return find_reply_cq_code(text)
    else:
        return False

# # 示例文本
# text1 = "[CQ:reply,id=785461647][CQ:at,qq=2221533105] 你好"
# text2 = "这是一段没有CQ码的文本"

# # 检测并处理CQ码
# result1 = check_reply_cq_code(text1)
# result2 = check_reply_cq_code(text2)

# print(result1)  
# print(result2)  