# -*- coding: utf-8 -*-
import argparse
import os
import sys
from time import sleep

from geteachinfo import geteachinfo
from spiderpub import spiderpub
import urllib.parse
from timevar import ProjectInfo, feedbacktime
from PDFHelper import PDFHelper

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

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description="pubmedsoso is python program for crawler article information and download pdf file",
        usage="python main.py keyword ")

    parser.add_argument('--version', '-v', action='version',
                        version=f'\nCurrent the {ProjectInfo.ProjectName}\n\n version: {ProjectInfo.VersionInfo}\n' +
                                f'Last updated date: {ProjectInfo.LastUpdate} \n' +
                                f'Author: {ProjectInfo.AuthorName} \n',
                        help='use --version to show the version')

    source_group = parser.add_mutually_exclusive_group(required=False)  # True?

    # source_group.add_argument("--script", '-s', action='store_true',
    #                           help='add --script -s arg running script mode',
    #                           default=False)

    parser.add_argument("keyword", type=str,
                        help='specify the keywords to search pubmed\n For example "headache"')


    parser.add_argument("--page_num", "-n", type=int,
                        help='add --number or -n to specify the page number you wanna to crawl'
                             'For example --number 10. Default number is 10',
                        default=10)

    parser.add_argument("--download_num", "-d", type=int,
                        help='add --download_num or -d to specify the doc number you wanna to download'
                             'For example -d 10. Default number is 10',
                        default=10)
    ####################################################################################################

    args = parser.parse_args()
    print("\n\n")

    if args.keyword.isspace() or args.keyword.isnumeric():
        print("pubmedsoso search keyword error\n")
        sleep(feedbacktime)
    
    
    print(f"当前使用的命令行参数 {args.__dict__}\n")
    print(f"当前使用的命令行参数 搜索关键词: \"{args.keyword}\", 文献信息检索数量: {args.page_num}, 文献下载数量:{args.download_num}\n")
    sleep(feedbacktime)
    
    
    print("是否要根据以上参数开始执行程序？y or n\n\n")
    startFlag = input()
    if startFlag == 'y' or startFlag == 'Y' or startFlag == 'Yes':
        pass
    if startFlag in ["n", "N", "No", "no"]:
        print("程序终止执行\n\n")
        sleep(feedbacktime)
        sys.exit()
        
    print('--' * 25, '\n')
    print("程序已运行，开始检查数据储存目录\n")
    print('--' * 25)
    sleep(0.5)
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
    sleep(feedbacktime)

    dbpath = "./pubmedsql"
    # ?term=cell%2Bblood&filter=datesearch.y_1&size=20


       # 根据上面输入的关键词初始化生成url参数
    search_param = Search_param(args.keyword)

    spiderpub(search_param.gen_search_param(), args.page_num)
    geteachinfo(dbpath)
    PDFHelper.PDFDonwloadEntry(args.download_num)
    os.system("pause")