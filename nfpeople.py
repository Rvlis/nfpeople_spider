from warnings import catch_warnings
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import csv
import re

# req = requests.get("http://www.nfpeople.com/")
# soup = BeautifulSoup(req, "lxml")

# nfpeople categories 1-25
# http://www.nfpeople.com/category/1?page=1

# from email import header
# import requests
# from bs4 import BeautifulSoup

# class NFPeople:
#     def __init__(self):
#        self.URL = 'http://www.nfpeople.com/category'
#        self.starnum = []
#        for start_num in range(1, 26):
#            self.starnum.append(start_num)
#        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}

#     def get_article_urls(self):
#         for start in self.starnum:
#             start = str(start)
#             html = requests.get(self.URL, params={'start':start},headers = self.header)
#             soup = BeautifulSoup(html.text,"html.parser")
#             name = soup.select('#content > div > div.article > ol > li > div > div.info > div.hd > a > span:nth-child(1)')
#             for name in name:
#                 print(name.get_text())

# if __name__== "__main__":
#     cls = Douban()
#     cls.get_top250()




def get_max_page_id(soup):
    try:
        sinfo = soup.find_all("div", attrs={"class":"v-paginator"})
        ainfo = sinfo[0].find_all('a')
        last = ainfo[len(ainfo)-1]
        pmax_url = last["href"]
        pmax = int(pmax_url[pmax_url.find("page=")+5:])
    except:
        pmax = 1

    return pmax

def get_article_urls(url, cid, category):
    url = url + "/" + str(cid)
    # html = requests.get(url, params={"page":pid}, headers=header)
    html = requests.get(url, headers=header)
    soup = BeautifulSoup(html.text, "lxml")
    pmax = get_max_page_id(soup)
    # print(pmax)
    urls = set()
    print("--------爬取 {} 类新闻链接--------".format(category))
    for pid in tqdm(range(1, pmax+1)):
        
        html = requests.get(url, params={"page":pid}, headers=header)
        soup = BeautifulSoup(html.text, "lxml")
        # print("pid is:", pid)
        ainfos = soup.select("div.leftbox.lists dl dt a")
        for ainfo in ainfos:
            # print(ainfo["href"])
            aurl = ainfo["href"]
            # print(aurl)
            urls.add(aurl)

    
    with open("./南方人物周刊/{}链接.txt".format(category), "w") as wf:
        for url in urls:    
            wf.write(url + "\n")

    return list(urls)


def get_article_contents(urls, category):
    a = re.compile(r'\n| |\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\t|\r')
    with open("./南方人物周刊/{}.csv".format(category), "w", newline="", encoding="gb18030") as wf:
        writer = csv.writer(wf, doublequote=False, escapechar="\\")
        writer.writerow(["标题", "来源", "概要", "内容", "链接"])
        print("--------爬取 {} 类新闻内容--------".format(category))
        for url in tqdm(urls):
            try:
                html = requests.get(url, headers=header)
                soup = BeautifulSoup(html.text, "lxml")
            except:
                continue
            # 标题
            try:
                title = soup.select("center h1")[0].get_text().strip()
            except:
                title = ""
            # 来源
            try:
                source = soup.select("p.source")[0].get_text().strip()
            except:
                source = ""
            # 概要
            try:
                summary = soup.select("p.summary em")[0].get_text().strip()
            except:
                summary = ""
            # 内容
            contents = soup.select("div.mainContent p")
            content = ""
            for item in contents:
                content += a.sub(' ', item.get_text())
            writer.writerow([title, source, summary, content, url])


if __name__ == "__main__":
    url = "http://www.nfpeople.com/category"

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
    
    # 类别共20种
    category_dict = {
        1:"封面人物1", 2:"报道", 3:"非虚构", 4:"图片故事", 5:"专栏",
        6:"后窗", 7:"评论", 8:"虚构", 9:"视觉", 10:"经典",
        11:"酷生活", 12:"封面人物2", 14:"世界观", 15:"历史", 16:"封面人物",
        21:"社会", 22:"商业", 23:"文化", 24:"明星", 25:"国际",
    }
    
    for cid in category_dict.keys():
        urls = get_article_urls(url, cid, category_dict[cid])
        get_article_contents(urls, category_dict[cid])
    # urls = ["http://www.nfpeople.com/article/10766"]
