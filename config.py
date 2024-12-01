# -*- coding: utf-8 -*-
import time

savetime = time.strftime("%Y%m%d%H%M%S")
feedbacktime: float = 1.5

# 这个参数用于geteachinfo决定一次性通过异步下载多少页面的信息，默认50啦
batchsize: int = 50


class ProjectInfo:
    VersionInfo: str = "1.1.8"
    ProjectName: str = "Pubmedsoso"
    LastUpdate: str = "20241130"
    AuthorName: str = "hiddenblue"
#此处的变量是main一次运行中需要多次调用的全局变量
