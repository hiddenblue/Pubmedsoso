# -*- coding: utf-8 -*-
import argparse
import os
import sys
from time import sleep

from geteachinfo import geteachinfo

from ExcelHelper import ExcelHelper
from GetSearchResult import spiderpub
from PDFHelper import PDFHelper
from WebHelper import WebHelper
from config import ProjectInfo, projConfig

feedbacktime = projConfig.feedbacktime


def printSpliter(length=25):
    print('--' * length, '\n')


if __name__ == '__main__':

    # 命令行参数解析
    parser = argparse.ArgumentParser(
        description="pubmedsoso is a python program for crawler article information and download pdf file",
        usage="python main.py keyword")

    parser.add_argument('-v', '--version', action='version',
                        version=f'\nCurrent the {ProjectInfo.ProjectName}\n\n version: {ProjectInfo.VersionInfo}\n' +
                                f'Last updated date: {ProjectInfo.LastUpdate} \n' +
                                f'Author: {ProjectInfo.AuthorName} \n',
                        help='use --version to show the version')

    source_group = parser.add_mutually_exclusive_group(required=False)  # True?

    ####################################################################################################

    # 下面几个是指定了可以使用的命令行参数 目前只支持三个
    # todo： 支持更多命令行参数选项

    parser.add_argument("keyword", type=str,
                        help='specify the keywords to search pubmed\n For example "headache"')

    parser.add_argument("-n", "--pagenum", type=int, metavar='',
                        help='add --pagenum or -n to specify the page number of info you wanna to crawl'
                             'For example --pagenum 10. Default number is 10',
                        default=10)

    parser.add_argument("-y", "--year", type=int, metavar='',
                        help='add --year or -y to specify year scale you would to search'
                             'For example --year 10. The Default is Not set',
                        default=None)

    parser.add_argument("-d", "--downloadnum", type=int, metavar='',
                        help='add --downloadnum or -d to specify the number of pdf you wanna to download'
                             'For example -d 10. Default number is 10',
                        default=10)
    
    parser.add_argument("-D", "--directory", type=str,  metavar='',
                        help='add --directory or -D specify the save path of pdf file'
                        'For example, -D ./output. Default path is ./document/pub'
                        'you can overrider the default path in config.py',
                        default='./document/pub')
    ####################################################################################################

    args = parser.parse_args()

    # print the hello info
    ProjectInfo.printProjectInfo()
    print("\n")
    
    # check the directory variable. the path variable from cli is preferred.
    # the default pdf saving directory path is from config.py which is './document/pub'
    if args.directory is not None:
        projConfig.pdfSavePath = args.directory

    if args.keyword.isspace() or args.keyword.isnumeric():
        print("pubmedsoso search keyword error\n")
        sleep(feedbacktime)



    print(f"Current commandline parameters: {args.__dict__}\n")
    print(
        f"当前使用的命令行参数 搜索关键词: \"{args.keyword}\", 文献信息检索数量: {args.pagenum}, 年份：{args.year}, 文献下载数量: {args.downloadnum}, 下载文献的存储目录: {projConfig.pdfSavePath}\n")
    try:
        result_num = WebHelper.GetSearchResultNum(args.keyword)
    except Exception as err:
        raise

    if os.getenv("DEBUG"):
        pass
    else:
        print("当前关键词在pubmed检索到的相关结果数量为: %s\n" % result_num)
        print("是否要根据以上参数开始执行程序？y or n\n")
        startFlag = input()
        if startFlag == 'y' or startFlag == 'Y' or startFlag == 'Yes':
            pass
        if startFlag in ["n", "N", "No", "no"]:
            print("程序终止执行\n\n")
            sleep(feedbacktime)
            sys.exit()

    printSpliter()
    print("程序已运行，开始检查数据储存目录\n")
    printSpliter()
    sleep(0.5)

    if os.path.exists(projConfig.pdfSavePath):
        print("文件储存目录检查正常，可以储存文件\n")
    else:
        os.makedirs(projConfig.pdfSavePath)
        print(f"成功在当前目录下建立 {projConfig.pdfSavePath} 文件夹\n")

    printSpliter()
    print(f"{projConfig.pdfSavePath} 目录检查完成，开始执行主程序\n")

    sleep(feedbacktime)

    dbpath = "./pubmedsql"
    # ?term=cell%2Bblood&filter=datesearch.y_1&size=20

    # 根据上面输入的关键词初始化生成url参数
    ParamDict = WebHelper.createParamDcit(args.keyword, args.year)
    encoded_param = WebHelper.encodeParam(ParamDict)

    # 从此处开始爬取数据

    printSpliter()

    spiderpub(encoded_param, args.pagenum, result_num)

    printSpliter()
    print("\n\n爬取搜索结果完成，开始执行单篇检索，耗时更久\n\n")

    geteachinfo(dbpath)

    printSpliter()
    print("\n\n爬取搜索结果完成，开始执行文献下载，耗时更久\n\n")

    # PDFHelper.PDFBatchDonwload(args.download_num)
    PDFHelper.PDFBatchDownloadEntry(args.downloadnum)

    ExcelHelper.PD_To_excel(dbpath, override=True)
    print("爬取最终结果信息已经自动保存到excel表格中，文件名为%s" % ExcelHelper.tablename)
    print(f"爬取的所有文献已经保存到{projConfig.pdfSavePath}目录下")
    print("爬取程序已经执行完成，自动退出, 哈哈，no errors no warning")

    printSpliter()
    sys.exit(0)
