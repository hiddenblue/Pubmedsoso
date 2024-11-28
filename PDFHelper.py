import random
import re
import time

import requests
from requests.exceptions import HTTPError, ConnectionError, ProxyError, ConnectTimeout

from DBHelper import DBWriter
from ExcelHelper import ExcelHelper
from geteachinfo import TempPMID, readdata1
from timevar import savetime


# 把一些关于PDF相关的操作抽象出来了，方便其他模块调用

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9034016/pdf/main.pdf

class PDFHelper:
    baseurl = "http://www.ncbi.nlm.nih.gov/"
    # 没有采用https是因为听说https的审查会增加延时
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9,en-GB;q=0.8,zh-CN;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    def __init__(self, dbpath):
        self.dbpath = dbpath

    @staticmethod
    def handle_error(e):
        print("Error occured: %s" % e)

    @classmethod
    def PDFDonwloadEntry(cls, limit):
        tablename = 'pubmed%s' % savetime
        count = 0
        dbpath = 'pubmedsql'
        PMID_list: [TempPMID] = readdata1(dbpath)

        PMCID_list = [item for item in PMID_list if item.PMCID != None]
        for item in PMCID_list:
            count += 1

            if count > limit:
                print("已达到需要下载的上限，下载停止\n")
                break
            print("开始下载第%d篇" % count)
            # result是从数据库获取的列表元组，其中的每一项构成为PMCID,doctitle
            html = PDFHelper.PDFdownload(item.PMCID)
            if html == None:
                print("网页pdf数据不存在，自动跳过该文献 PMCID为 %s" % item.PMCID)
                continue
            elif html == 1:
                print("30s超时,自动跳过该文献 PMCID为 %s" % item.PMCID)
                continue
            status = PDFHelper.PDFSave(html, item, dbpath)
            if status == None:
                print("保存pdf文件发生错误，自动跳过该文献PMCID为 %s" % item.PMCID)
                continue
            time.sleep(random.randint(0, 1))
        ExcelHelper.ToExcel(dbpath)  # 这里我把默认的数据库路径改成了全局变量dbpath
        print("爬取最终结果信息已经自动保存到excel表格中，文件名为%s" % tablename)
        print("爬取的所有文献已经保存到/document/pub/目录下")
        print("爬取程序已经执行完成，自动退出, 哈哈，no errors no warning")

    @classmethod
    def PDFdownload(cls, PMCID):

        # eventlet.monkey_patch()
        downloadUrl = cls.baseurl + "pmc/articles/" + PMCID + "/pdf/main.pdf"

        pdf_content = ""

        try:
            response = requests.get(downloadUrl, headers=cls.headers, timeout=30)
            if response.status_code == 200:
                pdf_content = response.content
                print("%s.pdf" % PMCID, "从目标站获取pdf数据成功")
            return pdf_content

        except (ProxyError, ConnectTimeout, ConnectionError, HTTPError) as e:
            cls.handle_error(e)
            print("%s.pdf" % PMCID, "从目标站获取pdf数据失败")
            return ""

        except Exception as e:
            cls.handle_error(e)
            print("%s.pdf" % PMCID, "从目标站获取pdf数据失败")
        return ""

    @staticmethod
    def PDFSave(html, tempid: TempPMID, dbpath):
        tablename = 'pubmed%s' % savetime
        # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了

        try:
            articleName = re.sub(r'[< > / \\ | : " * ?]', ' ', tempid.doctitle)
            # 需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
            savepath = "./document/pub/%s.pdf" % articleName
            file = open(savepath, 'wb')
            print("open success")
            file.write(html)
            file.close()
            # print("%s.pdf"%name,"文件写入到Pubmed/document/pub/下成功")
            print("pdf文件写入成功,文件ID为 %s" % tempid.PMCID, "保存路径为Pubmed/document/pub/")
            # 将pdf文件名称以及存储位置等相关信息添加到sqlite数据库当中
            try:
                writeSql = " UPDATE %s SET savepath = ? WHERE PMCID =?" % tablename
                param = (savepath, tempid.PMCID)
                DBWriter(dbpath, writeSql, param)

                print("pdf文件写入成功,文件ID为 %s" % tempid.PMCID,
                      "地址写入到数据库pubmedsql下的table%s中成功" % tablename)
                return True
            except:
                print("pdf文件保存路径写入到数据库失败")
        except:
            print("pdf文件写入失败,文件ID为 %s" % tempid.PMCID, "文件写入失败,检查路径")
