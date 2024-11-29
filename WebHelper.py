import urllib.parse
from typing import Optional

import requests
from lxml import etree
from requests.exceptions import HTTPError, ConnectionError, ProxyError, ConnectTimeout

from LogHelper import print_error


class WebHelper:
    # 这个类用来专门下载网页需要的html文件，不能作为pdf下载调用
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"
    }

    @classmethod
    def createParamDcit(cls, keyword):

        if " " in keyword:
            keyword = keyword.replace(" ", "%20")
        search_keywords_dict = {}
        search_keywords_dict['term'] = keyword.strip()
        return search_keywords_dict

    @staticmethod
    def encodeParam(param: dict) -> str:
        return urllib.parse.urlencode(param)

    @staticmethod
    def handle_error(e):
        print_error("Error occured: %s" % e)
    
    @staticmethod
    def getSearchHtml(parameter):
        # openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
        paramencoded = "?" + parameter
        try:
            SearchHtml = WebHelper.GetHTML(paramencoded)
            return SearchHtml
        except Exception as e:
            print_error("获取检索页失败，请检查输入的参数 %s\n" % e)

    @classmethod
    def GetHTML(cls, paramUrlEncoded: str, baseurl="https://pubmed.ncbi.nlm.nih.gov/") -> Optional[str]:

        """
        the default base_url is "https://pubmed.ncbi.nlm.nih.gov/"
        pay attention to you param
        
        if you would like to  get other site, fill with your target baseurl
        
        """

        request_url = cls.baseurl + paramUrlEncoded

        try:
            response = requests.get(request_url, headers=cls.headers)
            response.raise_for_status()
            html: str = response.content.decode("utf-8")
            return html

        except (ProxyError, ConnectTimeout, ConnectionError, HTTPError) as e:
            cls.handle_error(e)
            print_error("GetHTML requests Error: %s" % e)
            return None

        except Exception as e:
            print_error(f"请求失败: {e}")
            return None
    
    @staticmethod
    def GetSearchResultNum(keyword: str) -> int:
        # 根据上面输入的关键词初始化生成url参数
        ParamDict = WebHelper.createParamDcit(keyword)
        encoded_param = WebHelper.encodeParam(ParamDict)
        try:
            html = WebHelper.getSearchHtml(encoded_param)

            html_etree = etree.HTML(html)

            resultNumElem = html_etree.xpath(
                "//div[@id='search-results']/section[@class='search-results-list']//span[@class='value']/text()")
            if len(resultNumElem) != 0:
                return int(resultNumElem[0].replace(",", ""))
        except Exception as e:
            print_error("获取当前关键词搜索结果数量时出错: ", e)
            raise
            
        


if __name__ == "__main__":
    pass
