import asyncio
import re
import time
from pathlib import Path
from typing import Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from config import projConfig
from utils.DBHelper import DBWriter, DBFetchAllFreePMC
from utils.DataType import TempPMID
from utils.LogHelper import print_error, medLog

# 把一些关于PDF相关的操作抽象出来了，方便其他模块调用

# adjust the BATCH_SIZE in config.py according to your usage 
# the default pdf batch size is 5
BATCH_SIZE = projConfig.PDF_BatchSize


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
        print_error("Error occured: %s" % e)

    @staticmethod
    def __IsFileExist(path: str) -> bool:
        return Path(path).exists()

    @classmethod
    def __IsPDFExist(cls, tempid) -> bool:
        savepath = cls.__GetPDFSavePath(tempid)
        return PDFHelper.__IsFileExist(savepath)

    @classmethod
    def __GetPDFFileName(cls, tempid: TempPMID) -> str:
        return re.sub(r'[< >/\\|:"*?]', ' ', tempid.doctitle)

    @classmethod
    def __GetPDFSavePath(cls, tempid: TempPMID) -> str:
        return f"{projConfig.pdfSavePath}/{cls.__GetPDFFileName(tempid)}.pdf"

    @classmethod
    def PDFBatchDownloadEntry(cls, limit):
        """
        异步批量处理的pdf下载函数
        感觉写得稀烂啊
        """
        tablename = 'pubmed%s' % projConfig.savetime
        dbpath = 'pubmedsql'
        # 注意这个列表的数据类型，和名称并不是相符的
        # 这个返回的结果是有免费全文的，包括 FreeArticle 和 FreePMCArticle 两类
        free_article_list: [TempPMID] = DBFetchAllFreePMC(dbpath, tablename)

        free_pmc_list: [TempPMID] = [item for item in free_article_list if item.PMCID != ""]

        # 过滤掉已经存在于本地的文献
        target_pmc_list: [TempPMID] = []  # target pdf list to be downloaded

        for item in free_pmc_list:
            if cls.__IsPDFExist(item):
                # 存在于目录当中直接更新就行了
                cls.PDFUpdateDB(item, cls.__GetPDFSavePath(item), dbpath)
                medLog.info(f"PDF: {cls.__GetPDFFileName(item)} 在保存目录当中已存在，跳过下载")
                # 还没有下载就放到待下载列表当中
            else:
                target_pmc_list.append(item)

        # limit the dowload number
        # 这两个内容的index是相互对应的
        target_pmc_list: [TempPMID] = target_pmc_list[:limit]
        target_pmcid_list: [str] = [tempid.PMCID for tempid in target_pmc_list]

        # 不用担心输入和返回的匹配的位置对应问题
        pdf_list: [Optional[bytes]] = asyncio.run(cls.PDFBatchDonwloadAsync(target_pmcid_list))

        for index, pdf_content in enumerate(pdf_list):
            temppmid = target_pmc_list[index]
            if pdf_content is None:
                medLog.error("PMCID: %s 从目标站获取pdf数据失败" % temppmid.PMCID)
            else:

                status = PDFHelper.PDFSaveFile(pdf_content, temppmid)
                if status == True:
                    # 将pdf文件名称以及存储位置等相关信息添加到sqlite数据库当中
                    PDFHelper.PDFUpdateDB(temppmid, cls.__GetPDFSavePath(temppmid), dbpath)
                else:
                    medLog.error("保存pdf文件发生错误，自动跳过该文献PMCID为 %s" % temppmid.PMCID)
                    continue

    @classmethod
    async def PDFBatchDonwloadAsync(cls, PMCID_list: list[str]) -> list[Optional[bytes]]:
        """
        异步下载pmc文献的函数，以pdf_batchsize作为一次请求的量
        其中的pdf_batchsize可以通过config.py进行设置
        """

        pdf_list: list[Optional[bytes]] = []

        for i in range(0, len(PMCID_list), BATCH_SIZE):
            target = []
            if i + BATCH_SIZE > len(PMCID_list):
                target = PMCID_list[i:]
            else:
                target = PMCID_list[i:i + BATCH_SIZE]

            medLog.info(f"开始下载第 {i}-{i + len(target)}篇")
            async with aiohttp.ClientSession(timeout=ClientTimeout(30)) as session:
                start = time.time()

                tasks = [asyncio.create_task(cls.PDFdownloadAsync(session, PMCID)) for PMCID in target]
                results = await asyncio.gather(*tasks)
                end = time.time()

                medLog.info("PDFBatchDonwloadAsync takes %.2f seconds." % (end - start))
            pdf_list.extend(results)
        return pdf_list

    @classmethod
    async def PDFdownloadAsync(cls, session: ClientSession, PMCID: str) -> Optional[bytes]:
        downloadUrl = cls.baseurl + "pmc/articles/" + PMCID + "/pdf/main.pdf"
        semaphore = asyncio.Semaphore(5)

        async with semaphore:
            try:
                response = await session.get(downloadUrl, headers=cls.headers)
                content = await response.read()
                medLog.info("%s.pdf 从目标站获取pdf数据成功" % tempid)
                return content

            except (aiohttp.ClientResponseError, aiohttp.ClientHttpProxyError) as e:
                cls.handle_error(e)
                medLog.error("%s.pdf 从目标站获取pdf数据失败" % tempid)
                return None

            except Exception as e:
                cls.handle_error(e)
                medLog.error("%s.pdf 从目标站获取pdf数据失败" % tempid, )
                return None

    @classmethod
    def PDFSaveFile(cls, html: bytes, tempid: TempPMID) -> bool:
        """
        将pdf保存到本地文件的功能
        暂时还不确定能否支持异步，就先用同步版本了
        """
        # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了
        if html is None:
            return False

        try:
            articleName = cls.__GetPDFFileName(tempid)
            # 需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
            savepath = "%s/%s.pdf" % (projConfig.pdfSavePath, articleName)

            cls.FileSave(html, savepath)
            medLog.info("pdf文件写入成功,文件ID为 %s" % tempid.PMCID)
            medLog.info("保存路径为 %s" % projConfig.pdfSavePath)
            return True
        except Exception as e:
            medLog.error(f"pdf文件写入失败, 文件ID为 {tempid.PMCID}, 检查路径")
            medLog.error(e)
            return False

    @classmethod
    def FileSave(cls, content: bytes, savepath: str) -> bool:
        """
        一个方便将文件保存操作分离出来基础函数
        主要还是为独立的pdf下载函数服务的
        """
        try:
            file = open(savepath, 'wb')
            medLog.info("open success")
            file.write(content)
            file.close()
            medLog.info("文件写入成功", "保存路径为%s" % savepath)
            return True
        except Exception as e:
            medLog.error("文件写入失败", "保存路径为%s" % savepath)
            medLog.error(e)
            return False

    @classmethod
    def PDFUpdateDB(cls, tempid: TempPMID, savepath: str, dbpath: str) -> bool:
        tablename = 'pubmed%s' % projConfig.savetime
        try:
            writeSql = " UPDATE %s SET savepath = ? WHERE PMCID =?" % tablename
            param = (savepath, tempid.PMCID)
            DBWriter(dbpath, writeSql, param)

            medLog.info("pdf文件写入成功,文件ID为 %s" % tempid.PMCID)
            medLog.info("地址写入到数据库pubmedsql下的table%s中成功" % tablename)
            medLog.info("\n")
            return True
        except Exception as e:
            medLog.error("pdf文件保存路径写入到数据库失败: %s" % e)
            medLog.error("\n")
            return False


if __name__ == "__main__":
    pmcid = "PMC6817243"
    pmid = "35132177"
    "PMC3606786"
    "PMC8989886"
    dbpath = 'pubmedsql'

    tempid = TempPMID(doctitle="A rapid and efficientDNAextraction protocol from fresh and frozenhumanblood samples.",
                      PMCID=pmcid, PMID=pmid)
