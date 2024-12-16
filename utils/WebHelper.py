import asyncio
import time
import urllib.parse
from typing import Optional

import aiohttp
import requests
from aiohttp import ClientSession, ClientTimeout
from lxml import etree
from requests.exceptions import HTTPError, ConnectionError, ProxyError, ConnectTimeout

from utils.LogHelper import medLog


class WebHelper:
    # 这个类用来专门下载网页需要的html文件，不能作为pdf下载调用
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"
    }
    session = requests.Session()

    @classmethod
    def parseParamDcit(cls, **kwargs):
        """
        这个函数接受任意个数的参数作为字典使用，但是在使用的时候需要显式指定参数名称
        """

        search_keywords_dict = {}
        if 'keyword' in kwargs and kwargs['keyword']:
            search_keywords_dict['term'] = kwargs.get('keyword')

        if 'year' in kwargs and kwargs['year'] is not None:
            search_keywords_dict['filter'] = f'datesearch.y_{kwargs.get("year")}'

        # substitute the page size param with 50
        search_keywords_dict['size'] = 50

        return search_keywords_dict

    @classmethod
    def encodeParam(cls, param: dict) -> str:
        return urllib.parse.urlencode(param)

    @staticmethod
    def __handle_error(e):
        medLog.error("Error occured: %s" % e)

    @classmethod
    def getSearchHtml(cls, parameter: str):
        # openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
        paramencoded = "?" + parameter
        try:
            SearchHtml = WebHelper.GetHtml(cls.session, paramencoded)
            return SearchHtml
        except Exception as e:
            medLog.error("获取检索页失败，请检查输入的参数 %s\n" % e)

    @classmethod
    async def getSearchHtmlAsync(cls, parameter_list: list[str]) -> list[str]:
        """
        异步批量版本的getSearchHtml()， 传入的参数是list
        返回批量化的获取结果
        """
        parameter_list_encoded = ["?" + param for param in parameter_list]
        async with aiohttp.ClientSession(timeout=ClientTimeout(15)) as session:
            medLog.info(f"爬取第0-{len(parameter_list)}当中")
            start = time.time()
            # limit the semaphore
            tasks_search = [asyncio.create_task(cls.GetHtmlAsync(session, param_encode)) for param_encode in
                            parameter_list_encoded]
            results = await asyncio.gather(*tasks_search)
            end = time.time()

            medLog.info("getSearchHtmlAsync() takes %.2f seconds." % (end - start))
        return results

    @classmethod
    def GetHtml(cls, session, paramUrlEncoded: str, baseurl="https://pubmed.ncbi.nlm.nih.gov/") -> Optional[str]:

        """
        the default base_url is "https://pubmed.ncbi.nlm.nih.gov/"
        pay attention to you param
        
        if you would like to  get other site, fill with your target baseurl
        """
        request_url = cls.baseurl + paramUrlEncoded

        try:
            response = session.get(request_url, headers=cls.headers)
            response.raise_for_status()
            html: str = response.content.decode("utf-8")
            return html

        except (ProxyError, ConnectTimeout, ConnectionError, HTTPError) as e:
            cls.__handle_error(e)
            medLog.error("GetHTML requests Error: %s" % e)
            return None

        except Exception as e:
            medLog.error(f"请求失败: {e}")
            return None

    @staticmethod
    def GetSearchResultNum(**kwargs) -> int:
        # 根据上面输入的关键词初始化生成url参数
        paramDict: dict = WebHelper.parseParamDcit(**kwargs)
        encoded_param = WebHelper.encodeParam(paramDict)
        try:
            html = WebHelper.getSearchHtml(encoded_param)

            html_etree = etree.HTML(html)

            resultNumElem = html_etree.xpath(
                "//div[@id='search-results']/section[@class='search-results-list']//span[@class='value']/text()")
            if len(resultNumElem) != 0:
                return int(resultNumElem[0].replace(",", ""))
        except Exception as e:
            medLog.error("获取当前关键词搜索结果数量时出错: ", e)
            raise

    @classmethod
    async def GetHtmlAsync(cls, session: ClientSession, paramUrlEncoded: str,
                           baseurl="https://pubmed.ncbi.nlm.nih.gov/") -> Optional[str]:
        """
        异步改造后的html请求函数，基于asyncio和aiohttp包

        """
        request_url = cls.baseurl + paramUrlEncoded
        semaphore = asyncio.Semaphore(5)

        async with semaphore:
            try:
                response = await session.get(request_url, headers=cls.headers)
                content = await response.read()
                return content.decode("utf-8")

            except (aiohttp.ClientResponseError, aiohttp.ClientHttpProxyError) as e:
                cls.__handle_error(e)
                medLog.error("GetHTML requests Error: %s" % e)
                return None

            except Exception as e:
                cls.__handle_error(e)
                medLog.error("GetHTML requests Error: %s" % e)
                return None

    @classmethod
    async def GetAllHtmlAsync(cls, PMIDList: list[str]) -> list[str]:
        """
        是GetHtmlAsync的包装函数，
        一次性获取所有给定的html页面
        """
        # todo
        # 这个aiohttp访问的代码可以复用的
        try:
            async with aiohttp.ClientSession(timeout=ClientTimeout(30)) as session:
                # 这里设置了aiohttp的timeout属性
                start = time.time()
                tasks2 = [asyncio.create_task(cls.GetHtmlAsync(session, PMID)) for PMID in PMIDList]
                results = await asyncio.gather(*tasks2)
                end = time.time()
                medLog.info("GetAllHtmlAsync() takes %.2f seconds" % (end - start))
                return results
        except Exception as e:
            medLog.critical(" GetAllHtmlAsync:", e)
            raise


if __name__ == "__main__":
    pass
