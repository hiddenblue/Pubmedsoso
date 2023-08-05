# Pubmedsoso
  
  ![image](https://user-images.githubusercontent.com/62304226/167968328-753daa63-9087-4243-ad0b-b8a1b2ba0b0f.png)



一个自动批量提取pubmed文献信息和下载免费文献的小工具

## 主要功能：

自己写的基于简单的bs4和urllib的pubmed文献信息爬取和下载的爬虫，自动按照导入的链接，按你的要求下载指定数量的搜索结果文献

下载速度大概是10s一篇，同时能够提取文献的大部分信息，并自动生成excel文件，包括文献标题，摘要，关键词，作者名单，作者单位，是否免费，是不是review类型等信息

自动下载后，会将部分信息储存在本地的文本文件中，供参考，检索数据会储存在sqlite3数据库中，最后执行完成后，自动导出所有信息，生成一个Excel文件访问查看



## 依赖模块：



主要使用了bs4，re，xlwt，urllib

发布的版本中有pyintaller打包成的exe执行文件，如果需要自己在python环境运行则需要安装以下模块哦

需要导入的外部模块：

beautifulsoup4

eventlet 

xlwt==1.3.0

## 模块介绍：

main.py文件是整个项目运行的主要文件
spiderpub.py负责从pubmed检索页提取出所有的必要信息，储存到数据库和txt文本文件中
geteachinfo.py负责从数据库提取出spiderpub提取的信息，打开每个文献的单独页面，提取摘要和关键词等，获得pmcid，即文献下载地址信息
downpmc.py文件再次从数据库中提取出每个pmcid，打开页面对文献进行下载，储存，同时将保存路径储存到sqlite3数据库，最后将sqlite3中的提取的所有关于文献的信息导出到excel文件中。
  
timevar.py文件，里面含有一个在整个程序一次运行中，需要被所有模块都调用的信息，savetime，会被用于生成txt文件和excel文件名称，还有sqlite3中的table名称
 
save2excel.py文件是针对有时候爬虫没执行完又想导出信息的一个模块，独立于以上组件，只要有sql数据库和table就能查询保存成excel


## 使用方法：

1.克隆项目，在命令行环境下安装项目所需的依赖文件
```bash
git clone https://github.com/hiddenblue/Pubmedsoso.git
cd Pubmedsoso
pip install -r .\requirements.txt
```
当然，不方便安装git工具的话，可以手动下载zip文件夹运行
![image](https://github.com/hiddenblue/Pubmedsoso/assets/62304226/9efbf1e4-d4e3-4029-9754-07c3c2290d57)


2.在Windows terminal中切换到项目文件夹,执行**python main.py** 或者在直接执行exe可执行文件**pubmedsoso.exe**

```powershell
cd pubmedsoso # 切换到pubmedsoso文件夹
python main.py

#如果是使用打包好的exe文件
pubmedsoso.exe
```

等待文件夹检查完成后，出现关键词输入提示
输入需要爬取的关键词，比如“alzheimer's disease”(阿尔茨海默病）

![image](https://github.com/hiddenblue/Pubmedsoso/assets/62304226/a1fd581f-b2f9-4577-a507-c4cfb40e1de5)


*如果你熟悉IDE的话，可以在pycharm或者vscode等python环境下运行main.py*

3.然后按提示输入信息即可以，设置爬取信息页数和下载数量。需要注意的是，输入页数时，每页50个，建议数字不用设置得太大。
然后输入需要下载的文献数量，程序会从搜索结果中找到free pmc 免费文献，自动下载，这里下载速度取决你的网络状况。每个文献下载超过60s自动超时跳过，下载下一个。

**pubmedsoso会按照你正常搜索的顺序进行爬取下载**

![image](https://github.com/hiddenblue/Pubmedsoso/assets/62304226/841c1469-0d98-4025-9f72-33b5a4d8537c)


4.文献会自动下载到之前说的"document/pub/"下，同时会生成原始遍历信息的txt文件，程序最终执行完成会生成excel文件。

  
![image](https://user-images.githubusercontent.com/62304226/167930022-5b73d6b1-fca9-4012-99e6-18d06a1d1c52.png)


有问题可以联系我，估计bug还是挺多的，需求也可以改改，也请大家不要太过分的去爬取Pubmed

## save2excel模块

这个是方便大家在爬取之后，将历史信息导出到excel的模块，可以单独执行。
比如在IDE或者命令行中执行
`python save2excel.py`
![image](https://github.com/hiddenblue/Pubmedsoso/assets/62304226/49e58490-3acf-4843-88b9-e24d17b41628)

出现如上提示，可以选择sqlite3数据中的历史记录进行导出，会自动在本地生成一个导出的文件。

**不能有重复命名的excel文件，需要按提示删除**

## TO DO:

精确地搜索下载，这个还有点难

~~自定义关键词下载，这个未来应该会做，等我有空弄明白pubmed的检索参数url生成规则就行~~（已经实现）

对非免费文献的scihub自动补全下载

能用的gui界面

最好附带一个免费的百度翻译插件，有时候大家可能用得上

---------------------------------------------------------------------------------------
### 2022.5.16
更新了自动创建document/pub文件夹功能，不需要手动创建文件夹了，会自动检查和创建。

### 2023.08.05
更新修复了abstract爬取失败的bug，同时不再需要用户手动复制粘贴网页的参数了
