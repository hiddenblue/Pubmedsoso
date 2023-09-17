# -*- coding: utf-8 -*-
import os
from time import sleep

from downpmc import downpmc
from geteachinfo import geteachinfo
from spiderpub import spiderpub
import  yaml

print('--' * 25, '\n')
print("程序已运行，开始检查数据储存目录\n\n")
print('--' * 25)
sleep(1.5)
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

def main():

    parameter = str(input("请在下面粘贴你构建的搜索结果的parameter\n"))
    sleep(1)
    if parameter == '':
        print("输入有误\n")
    num1 = int(input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n"))
    sleep(1)
    if type(num1) != int:
        print("输入有误\n")
    limit = int(input("请输入爬取信息后你需要下载的文献数量\n"))
    sleep(1)

    spiderpub(parameter, num1)
    geteachinfo(dbpath)
    downpmc(limit)

class PubmedSoSo():

    def __init__(self, config_path):
        self.config_yaml = self.config_init()
        if self.config_yaml['use_mode'] == 'script':
            self.page_num = self.config_yaml['scipt_mode_args']['page_num'] #默认下载文献信息的页数
            self.download_num = self.config_yaml['scipt_mode_args']['download_num']  # 默认只下载一篇文献PDF
            self.search_keywords = self.config_yaml['scipt_mode_args']['search_keywords']  #这里我们可能要考虑多组关键词的情况 我们就用list格式，暂时不支持单独设置他们的参数
        else:
            self.testarg = self.config_yaml['command_mode_args']['test_arg']
        # 全局参数初始化，太多就不挨个初始化了，全整进去得了
        self.global_params = self.config_yaml['global_params']

    def config_init(self, config_path):
        with open(config_path, "r", encoding="utf-8") as fd:  # file descriptor
            config = fd.read()
        return yaml.load(config, Loader=yaml.FullLoader)

from




if __name__ == "__main__":
    config_path = "./config.yaml"   ## pubmedsoso配置文件的位置，默认和main.py在同一个文件夹下
    pubmedsoso = PubmedSoSo(config_path)

    dbpath = "./pubmedsql"
    main()
# ?term=cell%2Bblood&filter=datesearch.y_1&size=20
