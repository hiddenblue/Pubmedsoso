# -*- coding: utf-8 -*-
import shutil
import time

class ProjectInfo:
    VersionInfo: str = "1.2.1"
    ProjectName: str = "Pubmedsoso"
    LastUpdate: str = "20241212"
    AuthorName: str = "hiddenblue"

    @classmethod
    def printProjectInfo(cls):
        # 动态计算字段名称的最大宽度
        max_width = max(len(key) for key in cls.__dict__.keys() if not key.startswith("__"))

        # 获取终端宽度
        terminal_width = shutil.get_terminal_size().columns
        
        print("")
        # 打印居中的欢迎信息
        welcome_message = "欢迎使用 Pubmedsoso 文献检索工具"
        print("")

        print(welcome_message.center(terminal_width))
        
        # 打印分隔线
        print("=" * terminal_width)



        # 打印项目信息
        for key, value in cls.__dict__.items():
            if not key.startswith("__") and not callable(value) and not isinstance(value, classmethod):
                print(f"{key:<{max_width}}: {value}".center(terminal_width))

        # 打印分隔线
        print("=" * terminal_width)
        
class GlobalConfig:
    def __init__(self):
        self.savetime: str = time.strftime("%Y%m%d%H%M%S")
        self.feedbacktime: float = 1.5
        self.pdfSavePath: str = "./document/pub"

        # 这个参数用于geteachinfo决定一次性通过异步下载多少页面的信息，默认50啦
        self.batchsize: int = 50 


# 下面这句在从其他模块导入这个变量执行就会自动执行，并且是一个全局共享的状态
projConfig = GlobalConfig()

if __name__ == "__main__":
    
    ProjectInfo.printProjectInfo()