# -*- coding: utf-8 -*-
from spiderpub import spiderpub
from downpmc import downpmc
from geteachinfo import geteachinfo

def main():
    parameter = str(input("请在下面粘贴你构建的搜索结果的parameter\n"))
    if parameter == '':
        print("输入有误\n")
    num1 = int(input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n"))
    if type(num1) != int:
        print("输入有误\n")
    limit = int(input("请输入爬取信息后你需要下载的文献数量\n"))

    spiderpub(parameter, num1)
    geteachinfo()
    downpmc(limit)

main()
#?term=cell%2Bblood&filter=datesearch.y_1&size=20