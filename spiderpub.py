# -*- coding: utf-8 -*-
import random
import re
import sqlite3
import urllib
import urllib.request
from time import sleep

from bs4 import BeautifulSoup

from timevar import savetime


def opensearch(parameter):
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"
    url=baseurl+"?"+parameter
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read()
        return html
    # except urllib.error.URLError as e:
    #     if hasattr(e,"code"):
    #         print(e.code)
    #     if hasattr(e,"reason"):
    #         print(e.reason)
    except:
        print("获取检索页失败，请检查输入的参数\n")

# searchweb= opensearch(parameter).decode("utf-8")#使用Unicode8对二进制网页进行解码

#<span class="value">1,284</span>
#<label class="of-total-pages">of 26</label>

#这部分函数的功能主要是便利整个搜索页，后面可能做一个显示most recently结果的可选sort参数,默认每页50个结果

def traverse(html) -> list:
    global result_all
    findlink_title = re.compile(r'<a class="docsum-title".*?">.*?([A-Z0-9].*?)[.?]', re.S)  # 提取文章的title，含有</b>符号
    findlink_PMID = re.compile(r'<span class="citation-part".*>(\d+)<\/span>')  # 提取PMID号，作为下载的地址
    findlink_FREE_PMC_MARK = re.compile(r'<span class="free-resources.*?>(.*)\.<')  # 提取free pmc article标志
    # findlink4 = re.compile(r'<span class="value">(.+)<\/span>')
    # findlink5 = re.compile(r'(doi:.*?\.).?</span>')
    # findlink5 = re.compile(r'(doi:.*?\.)[ <]')#查找文献doi
    findlink_journal = re.compile(r'journal-citation">(.*?) doi:.*?\.[ <]')  # 查找期刊名称
    findlink_doi = re.compile(r'journal-citation">.*? (doi:.*?\.)[ <]')  # 查找文献doi
    findlink_auto_info = re.compile(r'full-authors">(.*?)<\/span>')  # 查找作者名称信息
    findlink_review = re.compile(r'citation-part">Review.<\/span>')  # 查找文献review标签

    try:
        content = BeautifulSoup(html, "html.parser")  # 通过bs4解析网页的内容，查找到页面有关于各个项目的信息
        result_all = int(str(content.find_all("span", class_="value")[0])[20:-7].replace(',', ''))
        print("当前关键词共有%d个搜索结果" % result_all)
        # print(result_all)
        # page_now = re.match(findlink4,str(content))
        # print(page_now)
        data = []
        for item in content.find_all("div", class_="docsum-content"):
            item = str(item)
            temp = []

            PMID = re.findall(findlink_PMID, item)[0]

            journal = re.search(findlink_journal, item)  # 少数文献是没有doi号的，直接用item[0]会导致index超出
            if journal == None:
                journal = ''
            else:
                journal = journal.group(1)
            print(journal)

            doi = re.search(findlink_doi, item)  # 少数文献是没有doi号的，直接用item[0]会导致index超出
            if doi == None:
                doi = ''
            else:
                doi = doi.group(1)
            print("文献doi号:%s" % doi)
            # 下面是获取作者名单#
            authorlist = re.search(findlink_auto_info, item)
            if authorlist != None:
                authorlist = authorlist.group(1)
            else:
                authorlist = ''

            # 下面是查找文献的title
            doctitle = re.findall(findlink_title, item)[0]
            # doctitle=doctitle.replace("<b>",'').replace("</b>",'').replace("<em>",'').replace("</em>",'').replace('<sup>','').replace("</sup>",'').replace("-/-",'')
            doctitle = doctitle.replace("-/-", '')
            doctitle = re.sub(r"<.+?>", '', doctitle)

            # 查找文献的期刊名称和分布的时间

            # 下面是freemark，分为两种类型，free pmc article和free article，没有的为空值
            # freemark flag: 0，不是免费文件无原文，1 是free article无原文， 2 是有pmc原文
            freemark = re.findall(findlink_FREE_PMC_MARK, item)
            print(freemark)
            print(len(freemark))
            if len(freemark) == 0:
                freemark = '0'
            else:
                if len(freemark[0]) == 16:
                    freemark = '2'
                else:
                    freemark = '1'
            # doctitle=doctitle.replace("</b>",'')

            # 下面是查找review标签，两种，空值或者有，即0或者1，1就是表示文章是review类型的
            reviewmark = re.search(findlink_review, item)
            # print(reviewmark.group())
            if reviewmark == None:
                reviewmark = '0'
            else:
                reviewmark = '1'
            temp.append(doctitle)
            temp.append(authorlist)
            temp.append(journal)
            temp.append(doi)
            temp.append(PMID)
            temp.append(freemark)
            temp.append(reviewmark)
            data.append(temp)
            print("当前data数据长度%d" % len(data))
            print('\n')
        return data
    except:
        print("遍历搜索页信息失败\n")


# file=open("pubmed.txt","w",encoding="utf-8")

def createdb(dbpath: str):  # 创建一个数据库
    tablename = 'pubmed%s' % savetime
    print(tablename)

    sql = '''
    create table %s
    (id  integer primary key autoincrement,
    doctitle text,authorlist text,journal text,doi text,PMID numeric,PMCID numeric,abstract text,
    keyword text,affiliations text,freemark numeric,reviewmark numeric,savepath text)''' % tablename
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    conn.close()
    print("创建数据库成功 ID:%d\n" % cursor.lastrowid)


def save2sql(datalist, dbpath: str):  # 构建一个保存检索数据的sqlite数据库
    tablename = 'pubmed%s' % savetime
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    for data in datalist:
        try:
            for index in range(len(data)):
                # data[index]=data[index].replace('''"''',"''")
                # data[index]='"'+data[index]+'"'
                print(data[index])
            print(len(data))

            # sql="""
            # insert into pubmed(
            # doctitle,authorlist,journal,doi,PMID,freemark,reviewmark)
            # values(%s,%s,%s,%s,%s,%s,%s)"""%(data[0],data[1],data[2],data[3],data[4],data[5],data[6])
            # sql="""
            # insert into pubmed(
            # doctitle,authorlist,journal,doi,PMID,freemark,reviewmark)
            # values("{}","{}","{}","{}","{}","{}",{})""".format(
            #     data[0].replace('''"''',''''''''),data[1],data[2],data[3],data[4],data[5],data[6])
            sql="""
            insert into "{}"(
            doctitle,authorlist,journal,doi,PMID,freemark,reviewmark)
            values("{}","{}","{}","{}","{}","{}",{})""".format(
                tablename,data[0].replace('''"''',''''''''),data[1],data[2],data[3],data[4],data[5],data[6])
            cursor.execute(sql)
            print("写入数据库成功\n")
        except:
            print("当前项目写入失败\n")
            continue
    conn.commit()
    cursor.close()

# dbpath=parameter[0:10]
# print(dbpath )

# file=open("ifnar2.html","rb")
# traverse(file)
# file.close()

def spiderpub(parameter: str, num1: int):
    size = re.search('&size=(\d{1,3})', parameter)
    if size == None:
        parameter += '&size=50'
    parameter = re.sub(r'&size=(\d{1,3})', '&size=50', parameter)
    page_count = 0
    datalist = []
    result_all_num = -1
    pagemax = 1
    for i in range(1, num1 + 1):
        # 开始遍历每一页结果，一共num页最大pagemax页
        if i > pagemax:
            print("已遍历所有页\n")
            break
        parameter = parameter + "&page=" + str(i)
        try:
            html = opensearch(parameter)
            if html == None:
                print("检索页获取出错，即将退出\n")
                break
            data = traverse(html)
            if data==None:
                print("遍历检索页信息出错，当前检索页为%d(每页50个结果)\n"%i)
            datalist.extend(data)
            pagemax = (result_all + 49) // 50
            sleep(random.randint(0, 2))
            print("已爬取完第%d页\n" % i)
            # print(datalist)
        except:
            print("spiderpub函数出错，请检查结果\n")
    dbpath = 'pubmedsql'
    createdb(dbpath)
    save2sql(datalist, dbpath)
    txtname="pubmed%s.txt"%savetime
    file = open(txtname, "w", encoding='utf-8')
    for item in datalist:
        output = ''
        for j in item:
            output = output + str(j) + ' '
        output = output + '\n'
        file.write((output))
    file.close
#
# def savetime():
#     savetime = time.strftime("%Y%m%d%H%M%S")
#     file=open('./globalvar.txt',"r",encoding='utf-8')
#     f=file.read()












