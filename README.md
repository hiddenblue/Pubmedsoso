# Pubmedsoso
一个批量下载pubmed免费文献的python小工具
自己写的基于简单的bs4和urllib的pubmed文献信息爬取和下载的爬虫
主要使用了bs4，re，xlwt，urllib这些模块

发布的版本中有pyintaller打包成的exe执行文件

需要导入的外部模块：
beautifulsoup4
eventlet 
importlib-metadata==4.11.3
pefile==2021.9.3
xlwt==1.3.0

使用方法：

1.打开pubmed，https://pubmed.ncbi.nlm.nih.gov/

在pubmed搜点你想要的东西，比如我以关键词“alzheimer's disease”(阿尔茨海默病）为关键词进行检索



![image](https://user-images.githubusercontent.com/62304226/167921781-75c5a0f0-3e02-468f-975d-99d38b1edef9.png)



2.将地址栏中位于nih.gov/后的参数复制下来，比如我这里是“?term=alzheimer%27s+disease&filter=datesearch.y_5&size=20”




![image](https://user-images.githubusercontent.com/62304226/167921897-f203dad2-cbb8-4294-96bf-27c101c91c68.png)
 
   
  

3.打开文件夹，看到pubmedsoso.exe可执行文件后，确保它所在的目录下有document文件夹，文件夹里有pub子文件夹，就像这样，没有就手动创建吧。
 

  
![image](https://user-images.githubusercontent.com/62304226/167922254-d533dae7-7c0e-4b80-8953-4037b92c6c04.png)

  
  
4.直接执行exe文件，或者在命令行中运行，或者在pycharm或者vscode等python环境下运行main.py

5.显示“请在下面粘贴你构建的搜索结果的parameter”后，按提示输入信息即可以，需要注意的是，输入页数时，每页50个，如果数字太大，对服务器造成负担可能会导致ip被封（暂未发现），建议控制在
20页以下。
然后输入需要下载的文献数量，程序会从搜索结果中找到free pmc 免费文献，自动下载，这里下载速度取决你的网络状况。每个文献下载超过60s自动超时跳过，下载下一个。

6.文献会自动下载到之前说的"document/pub/"下，同时会生成原始遍历信息的txt文件，程序最终执行完成会生成excel文件。

有问题可以联系我，估计bug还是挺多的，需求也可以改改

TO DO:

对非免费文献的scihub自动补全下载
能用的gui界面
最好附带一个免费的百度翻译插件，有时候大家可能用得上

