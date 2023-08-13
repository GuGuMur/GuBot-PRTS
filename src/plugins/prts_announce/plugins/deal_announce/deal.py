import re
from bs4 import BeautifulSoup
from httpx import AsyncClient


async def firstDeal(id: str) -> dict[str, str]:
    async with AsyncClient() as client:
        res = await client.get(f"https://ak-webview.hypergryph.com/api/game/bulletin/{id}")
        res = res.json()["data"]
    return {"title": res["header"].replace("/n",""), "content": res["content"]}


async def announceDealt(name: str, text: str):
    picname = "活动预告 " + name

    text = text.replace("</p>", "</p>\n")
    text = re.sub(r"\<strong\>(.*?)\</strong\>", r"'''\1'''", text)  # 去strong
    text = re.sub(r"\<p\>(.*?)\</p\>", r"\1\n", text)  # 去p
    text = re.sub(r'<div class="media-wrap image-wrap">(.*?)</div>', r"\1", text) #去img的div包裹 
    text = re.sub(r'<span style="color:(#.*?)">(.*?)</span>', r"{{color|\1|\2}}", text)#转color
    text = text.replace('<p style="text-align:left;"></p>',"")

    #img处理
    soup = BeautifulSoup(text, "html.parser")
    img_dict = {}
    img_tags = soup.find_all("img")
    for i, img_tag in enumerate(img_tags):
        img_src = img_tag["src"]
        # 处理yj URL图片不带后缀的情况
        pic_name_src = img_tag["src"]
        if not re.search(r'\.(jpg|jpeg|png|gif)$', img_src, re.I):
            pic_name_src += '.jpg'
        
        img_wiki_name = f'{picname} {str(i+1).zfill(2)}.{pic_name_src.split(".")[-1]}'
        img_dict[img_wiki_name] = {"src": img_src, "suffix": img_src.split(".")[-1]}
        text = text.replace(str(img_tag), f"[[文件:{img_wiki_name}|760px]]\n\n")
    return {"wikitext": text.strip(), "img": img_dict}
