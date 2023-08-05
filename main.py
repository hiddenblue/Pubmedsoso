# -*- coding: utf-8 -*-
import os
from time import sleep

from downpmc import downpmc
from geteachinfo import geteachinfo
from spiderpub import spiderpub
import urllib.parse

class Search_param(str):
    """
    可以由generate方法encode生成初次检索所需的URL后缀
    例如：”?term=alzheimer%27s+disease“
    可以附加一些调整网页的属性
    """
    def __init__(self, keywords:str):
        self.search_keywords = {}
        self.search_keywords['term'] = keywords.strip()

    def gen_search_param(self) -> str:
        # encode url生成request需要的url
        return urllib.parse.urlencode(self.search_keywords)

    def specify_web_size(self, size: int):
        # 调整 搜索页面的大小
        self.search_keywords['size'] = size

    def specify_any_param(self, key: str, value):
        """
        针对任意参数进行调整, 需要提供合适的键值对，默认不存在
        目前观察到的有：sort(date, pubdate, fauth, jour), sort_order(asc) 更多参数请查看pubmed的搜索URL
        :param key: url链接需要添加的键
        :param value: url链接中键对应的值
        :return:
        """
        self.search_keywords[key] = value

print('--' * 25, '\n')
print("程序已运行，开始检查数据储存目录\n\n")
print('--' * 25)
sleep(1.5)
if os.path.exists('./document'):
    if os.path.exists('./document/pub'):
        print("文件储存目录检查正常，可以储存文件\n")
    else:
        os.makedirs('./document/pub')
        print("成功在当前目录下建立/document/pub文件夹\n")
else:
    os.makedirs('./document/pub')
    print("成功在当前目录下建立/document/pub文件夹\n")
print('--'*25,'\n')
print("document/pub目录检查完成，开始执行主程序\n")
print('--'*25,'\n')

def main():
    search_key = ""
    while(search_key == ""):
        search_key = str(input("请在下面你想要爬取的搜索关键词\n"))
        sleep(1)
        if search_key == '':
            print("输入有误, 请重新输入\n")
    num1 = int(input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n"))
    sleep(1)
    if type(num1) != int:
        print("输入有误\n")
    limit = int(input("请输入爬取信息后你需要下载的文献数量\n"))
    sleep(1)

    # 根据上面输入的关键词初始化生成url参数
    search_param = Search_param(search_key)

    spiderpub(search_param.gen_search_param(), num1)
    geteachinfo(dbpath)
    downpmc(limit)


dbpath = "./pubmedsql"
main()
# ?term=cell%2Bblood&filter=datesearch.y_1&size=20
os.system("pause")
