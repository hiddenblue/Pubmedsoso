# -*- coding: utf-8 -*-
import os
from time import sleep

from downpmc import downpmc
from geteachinfo import geteachinfo
from spiderpub import spiderpub

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

    parameter = str(input("请在下面粘贴你构建的搜索结果的parameter\n"))
    sleep(1)
    if parameter == '':
        print("输入有误\n")
    num1 = int(input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n"))
    sleep(1)
    if type(num1) != int:
        print("输入有误\n")
    limit = int(input("请输入爬取信息后你需要下载的文献数量\n"))
    sleep(1)

    spiderpub(parameter, num1)
    geteachinfo(dbpath)
    downpmc(limit)


dbpath = "./pubmedsql"
main()
# ?term=cell%2Bblood&filter=datesearch.y_1&size=20
