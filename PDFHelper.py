import asyncio
import re
import time
from pathlib import Path
from typing import Optional

import aiohttp
import requests
from aiohttp import ClientSession, ClientTimeout

from DBHelper import DBWriter, DBFetchAllFreePMC
from DataType import TempPMID
from LogHelper import print_error
from config import savetime, pdfSavePath


# 把一些关于PDF相关的操作抽象出来了，方便其他模块调用

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9034016/pdf/main.pdf

class PDFHelper:
    baseurl = "http://www.ncbi.nlm.nih.gov/"
    session = requests.Session()
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
        print_error("Error occured: %s" % e)

    @staticmethod
    def IsFileExist(path: str) -> bool:
        return Path(path).exists()

    @classmethod
    def IsPDFExist(cls, tempid) -> bool:
        savepath = cls.GetPDFSavePath(tempid)
        return PDFHelper.IsFileExist(savepath)

    @classmethod
    def GetPDFFileName(cls, tempid: TempPMID) -> str:
        return re.sub(r'[< >/\\|:"*?]', ' ', tempid.doctitle)

    @classmethod
    def GetPDFSavePath(cls, tempid: TempPMID) -> str:
        return f"{pdfSavePath}/{cls.GetPDFFileName(tempid)}.pdf"

    @classmethod
    def PDFBatchDownloadEntry(cls, limit):
        """
        异步批量处理的pdf下载函数
        感觉写得稀烂啊
        """
        tablename = 'pubmed%s' % savetime
        count = 0
        dbpath = 'pubmedsql'
        PMID_list: [TempPMID] = DBFetchAllFreePMC(dbpath, tablename)

        temp_list = [item for item in PMID_list if item.PMCID != ""]

        # 过滤掉已经存在于本地的文献
        PMCID_list = []
        for item in temp_list:
            if cls.IsPDFExist(item):
                # 存在于目录当中直接更新就行了
                cls.PDFUpdateDB(item, cls.GetPDFSavePath(item), dbpath)
                print(f"PDF: {cls.GetPDFFileName(item)} 在保存目录当中已存在，跳过下载")
            else:
                PMCID_list.append(item)

        # limit the dowload number
        PMCID_list = PMCID_list[:limit]
        pdf_list = asyncio.run(cls.PDFBatchDonwloadAsync(PMCID_list))

        for item in pdf_list:
            if item[1] == None:
                print_error("%s.pdf" % item[1], "从目标站获取pdf数据失败")
            else:
                status = PDFHelper.PDFSaveFile(item[1], item[0])
                if (status == True):
                    # 将pdf文件名称以及存储位置等相关信息添加到sqlite数据库当中
                    PDFHelper.PDFUpdateDB(item[0], cls.GetPDFSavePath(item[0]), dbpath)
                else:
                    print_error("保存pdf文件发生错误，自动跳过该文献PMCID为 %s" % item[0].PMCID)
                    continue

    @classmethod
    async def PDFBatchDonwloadAsync(cls, PMCID_list: list[TempPMID]) -> list[tuple[TempPMID, Optional[bytes]]]:
        pdf_batchsize = 5

        pdf_list: list[tuple[TempPMID, Optional[bytes]]] = []

        for i in range(0, len(PMCID_list), pdf_batchsize):
            target = []
            if (i + pdf_batchsize > len(PMCID_list)):
                target = PMCID_list[i:]
            else:
                target = PMCID_list[i:i + pdf_batchsize]

            print(f"开始下载第 {i}-{i + len(target)}篇")
            async with aiohttp.ClientSession(timeout=ClientTimeout(30)) as session:
                start = time.time()

                tasks = [asyncio.create_task(cls.PDFdownloadAsync(session, tempPMID)) for tempPMID in target]
                results = await asyncio.gather(*tasks)
                end = time.time()

                print("PDFBatchDonwloadAsync takes %.2f seconds." % (end - start))
            pdf_list.extend(results)
        return pdf_list

    @classmethod
    async def PDFdownloadAsync(cls, session: ClientSession, tempid: TempPMID) -> tuple[TempPMID, Optional[bytes]]:
        downloadUrl = cls.baseurl + "pmc/articles/" + tempid.PMCID + "/pdf/main.pdf"
        semaphore = asyncio.Semaphore(5)

        async with semaphore:
            try:
                response = await session.get(downloadUrl, headers=cls.headers)
                content = await response.read()
                print("%s.pdf" % tempid, "从目标站获取pdf数据成功")
                return tempid, content

            except (aiohttp.ClientResponseError, aiohttp.ClientHttpProxyError) as e:
                cls.handle_error(e)
                print_error("%s.pdf" % tempid, "从目标站获取pdf数据失败")
                return tempid, None

            except Exception as e:
                cls.handle_error(e)
                print_error("%s.pdf" % tempid, "从目标站获取pdf数据失败")
                return tempid, None

    @classmethod
    def PDFSaveFile(cls, html, tempid: TempPMID) -> bool:
        """
        将pdf保存到本地文件的功能
        暂时还不确定能否支持异步，就先用同步版本了
        """
        tablename = 'pubmed%s' % savetime
        # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了

        try:
            articleName = cls.GetPDFFileName(tempid)
            # 需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
            savepath = "%s/%s.pdf" % (pdfSavePath, articleName)
            file = open(savepath, 'wb')
            print("open success")
            file.write(html)
            file.close()
            print("pdf文件写入成功,文件ID为 %s" % tempid.PMCID, "保存路径为%s" % pdfSavePath)
            return True
        except:
            print_error(f"pdf文件写入失败, 文件ID为 {tempid.PMCID}, 检查路径")
            return False

    @classmethod
    def PDFUpdateDB(cls, tempid: TempPMID, savepath: str, dbpath: str) -> bool:
        tablename = 'pubmed%s' % savetime
        try:
            writeSql = " UPDATE %s SET savepath = ? WHERE PMCID =?" % tablename
            param = (savepath, tempid.PMCID)
            DBWriter(dbpath, writeSql, param)

            print("pdf文件写入成功,文件ID为 %s" % tempid.PMCID,
                  "地址写入到数据库pubmedsql下的table%s中成功" % tablename)
            return True
        except Exception as e:
            print_error("pdf文件保存路径写入到数据库失败: ", e)
            return False


if __name__ == "__main__":
    pmcid = "PMC6817243"
    pmid = "35132177"
    "PMC3606786"
    "PMC8989886"
    dbpath = 'pubmedsql'

    tempid = TempPMID(doctitle="A rapid and efficientDNAextraction protocol from fresh and frozenhumanblood samples.",
                      PMCID=pmcid, PMID=pmid)
