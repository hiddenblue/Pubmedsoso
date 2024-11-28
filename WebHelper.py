import requests
from requests.exceptions import HTTPError, ConnectionError, ProxyError, ConnectTimeout


class WebHelper:
    # 这个类用来专门下载网页需要的html文件，不能作为pdf下载调用
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"
    }

    @staticmethod
    def handle_error(e):
        print("Error occured: %s" % e)

    @classmethod
    def GetHTML(cls, paramUrlEncoded: str, baseurl="https://pubmed.ncbi.nlm.nih.gov/"):

        """
        the default base_url is "https://pubmed.ncbi.nlm.nih.gov/"
        pay attention to you param
        
        if you would like to  get other site, fill with your target baseurl
        
        """
        
        request_url = cls.baseurl + paramUrlEncoded

        try:
            response = requests.get(request_url, headers=cls.headers)
            response.raise_for_status()
            html = response.content.decode("utf-8")
            return html

        except (ProxyError, ConnectTimeout, ConnectionError, HTTPError) as e:
            cls.handle_error(e)
            print("GetHTML requests Error: %s" % e)
            return ""

        except Exception as e:
            print(f"请求失败: {e}")
            return ""
