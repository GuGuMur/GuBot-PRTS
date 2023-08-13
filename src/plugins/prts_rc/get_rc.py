import feedparser
from urllib.parse import urlparse, parse_qs
async def topic_rc() -> list:
    '''用于生成PRTS中topic页面的最近更改'''
    # 全局变量
    entries = []
    group_member_list = ["永暮","NAAKII","AMUKnya","翱翔","爱吃鱼的牙同学","Enko","咕咕mur","Hjhk258","N2","RaYmondCheung","Visu2209","调零修罗","冬灵血巫大師","Xkzl"]
    # topic部分处理
    topic = "https://prts.wiki/api.php?urlversion=2&days=1&limit=50&action=feedrecentchanges&feedformat=atom&namespace=2600"
    topic = feedparser.parse(topic,request_headers = {"User-Agent": "GuGuMur-GuBotFastAPI/1.0"})
    for i in topic.entries:
        if i['author'] not in group_member_list:
            cell = {
                'title' : i['title'],
                'link': i['link'],
                'author': i['author'],
                'updated': i['updated'],
                'type': "topic"
            }
            entries.append(cell)
    # 非topic的讨论处理
    for talk_ns in ["1"]:
        talk = talk = "https://prts.wiki/api.php?urlversion=2&days=1&limit=50&action=feedrecentchanges&feedformat=atom&namespace="+talk_ns
        talk = feedparser.parse(talk,request_headers = {"User-Agent": "GuGuMur-GuBotFastAPI/1.0"})
        for i in talk.entries:
            if i['author'] not in group_member_list:
                url_params = parse_qs(urlparse(i['link']).query)
                title = url_params['title'][0]+"&diff="+url_params['diff'][0]+"&oldid="+url_params['oldid'][0]
                cell = {
                    'title' : title,
                    'link': i['link'],
                    'author': i['author'],
                    'updated': i['updated'],
                    'type': "talkdiff"
                }
                entries.append(cell)
    return sorted(entries, key=lambda entry: entry['updated'], reverse=True)