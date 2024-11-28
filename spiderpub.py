# -*- coding: utf-8 -*-
import random
import re
from time import sleep
import os
from lxml import etree
from DataType import SingleSearchData, ArticleFreeType

import DBHelper
from timevar import savetime
from WebHelper import WebHelper
from DataType import SingleSearchData

def getSearchHtml(parameter):
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    paramencoded = "?"+parameter
    try:
        SearchHtml = WebHelper.GetHTML(paramencoded)
        return SearchHtml
    except Exception as e:
        print("获取检索页失败，请检查输入的参数\n")

# searchweb= opensearch(parameter).decode("utf-8")#使用Unicode8对二进制网页进行解码

#这部分函数的功能主要是便利整个搜索页，后面可能做一个显示most recently结果的可选sort参数,默认每页50个结果

def traverse(html: str, resultNum) -> list[SingleSearchData]:
    #这部分函数的功能主要是便利整个搜索页，后面可能做一个显示most recently结果的可选sort参数,默认每页50个结果

    if os.getenv("DEBUG"):
        parser = etree.HTMLParser()
        html_etree = etree.parse("./searchresult.html", parser)
    else:
        html_etree = etree.HTML(html)

    resultNumElem = html_etree.xpath("//div[@id='search-results']/section[@class='search-results-list']//span[@class='value']/text()")
    if len(resultNumElem) != 0:
        resultNum = int(resultNumElem[0].replace(",", ""))
    else:
        return []
    print("当前关键词共有%d个搜索结果" % resultNum)

    ret = []
    try:
        AllSearchElem = html_etree.xpath("(//div[@class='docsum-content'])")
        print(len(AllSearchElem))

        for index, singleSearchElem in enumerate(AllSearchElem):
            print(index+1)

            #1.doc title
            xpath_expression = './/a[@class="docsum-title"]/text() | .//a[@class="docsum-title"]//b/text()'
            doctitleElem = singleSearchElem.xpath(xpath_expression)

            print(doctitleElem)
            doctitle = "".join([item.strip() for item in doctitleElem if item.strip()])
            print("doctitle: ", doctitle)

            # 2.short_author
            short_author = singleSearchElem.xpath(".//span[@class='docsum-authors short-authors']/text()")
            if len(short_author) != 0:
                short_author = short_author[0]
            print("short_author: ", short_author)

            # 3.full_author
            full_author = singleSearchElem.xpath(".//span[@class='docsum-authors full-authors']/text()")
            if len(full_author) != 0:
                full_author = full_author[0]
            print("full_author: ",full_author)

            # 4.short_journal
            short_journal = singleSearchElem.xpath(".//span[@class='docsum-journal-citation short-journal-citation']/text()")
            if len(short_journal) != 0:
                short_journal = short_journal[0]

            # 5.full_journal
            full_journal = singleSearchElem.xpath(".//span[@class='docsum-journal-citation full-journal-citation']/text()")
            if len(full_journal) != 0:
                full_journal = full_journal[0]

            print("short_journal: ", short_journal)
            print("full_journal: ", full_journal)

            # 6.PMID
            PMID = singleSearchElem.xpath(".//span[@class='docsum-pmid']/text()")
            print(PMID)

            # 7.freemark
            # 下面是freemark，分为两种类型，free pmc article和free article，没有的为空值
            # freemark flag: 0，不是免费文件无原文，1 是free article无原文， 2 是有pmc原文
            freePMCMarkElem = singleSearchElem.xpath(".//span[@class='free-resources spaced-citation-item citation-part']/text()")
            print(freePMCMarkElem)

            if len(freePMCMarkElem) == 0:
                FreeMark = ArticleFreeType.NoneFreeArticle
            else:
                if "Free PMC article" in freePMCMarkElem[0]:
                    FreeMark = ArticleFreeType.FreePMCArticle
                elif "Free article" in freePMCMarkElem[0]:
                    FreeMark = ArticleFreeType.FreeArticle
                else:
                    FreeMark = ArticleFreeType.NoneFreeArticle

                # 8.reviewMark
            # 下面是查找review标签，两种，空值或者有，即0或者1，1就是表示文章是review类型的
            reviewMark = singleSearchElem.xpath(".//span[@class='publication-type spaced-citation-item citation-part']/text()")
            if reviewMark == None:
                reviewMark = False
            else:
                reviewMark = True
            print("reviewMark: ", reviewMark)

            # the doi search is put off to individual page


            ret.append(SingleSearchData(doctitle=doctitle,
                                        short_journal=short_journal,
                                        full_journal=full_journal,
                                        short_author=short_author,
                                        full_author=full_author,
                                        PMID=PMID,
                                        freemark=FreeMark,
                                        reviewmark=reviewMark))
            print("当前data数据长度%d\n" % len(ret))
        return ret
    except Exception as e:
        print("遍历搜索页信息失败: %s\n"%e)
        return []


# file=open("pubmed.txt","w",encoding="utf-8")

def SaveSearchData(datalist: list[SingleSearchData], dbpath: str):  # 构建一个保存检索数据的sqlite数据库
    tablename = 'pubmed%s' % savetime
    for singleSearchData in datalist:
        try:
            print(singleSearchData)
            
            """
                doctitle: str
                short_author: str
                full_author: str
                short_journal: str
                full_journal: str
                PMID: str
                freemark: ArticleFreeType
                reviewmark: bool
            """

            sql = f"""
            INSERT INTO {tablename} (
                doctitle, short_author, full_author, short_journal, full_journal,  PMID, freemark, reviewmark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            writeparam = (singleSearchData.doctitle,
                          singleSearchData.short_author,
                          singleSearchData.full_author,
                          singleSearchData.full_journal,
                          singleSearchData.short_journal,
                          singleSearchData.PMID,
                          singleSearchData.freemark,
                          singleSearchData.reviewmark)
            
            DBHelper.DBWriter(dbpath, sql, writeparam)
        except Exception as e:
            print("当前项目写入失败: %s\n", e)
            continue

def spiderpub(parameter: str, num1: int):
    size = re.search('&size=(\d{1,3})', parameter)
    if size == None:
        parameter += '&size=50'
    parameter = re.sub(r'&size=(\d{1,3})', '&size=50', parameter)
    page_count = 0
    datalist = []
    result_all_num = -1
    pagemax = 1
    resultNum = 0
    for i in range(1, num1 + 1):
        # 开始遍历每一页结果，一共num页最大pagemax页
        if i > pagemax:
            print("已遍历所有页\n")
            break
        parameter = parameter + "&page=" + str(i)
        try:
            html = getSearchHtml(parameter)
            if html == None:
                print("检索页获取出错，即将退出\n")
                break
            SingleSearchPageData = traverse(html, resultNum)
            if SingleSearchPageData==None:
                print("遍历检索页信息出错，当前检索页为%d(每页50个结果)\n"%i)
            datalist.extend(SingleSearchPageData)
            pagemax = (resultNum + 49) // 50
            sleep(random.randint(0, 1))
            print("已爬取完第%d页\n" % i)
            # print(datalist)
        except:
            print("spiderpub函数出错，请检查结果\n")
    dbpath = 'pubmedsql'
    DBHelper.DBCreater(dbpath)
    DBHelper.DBTableCreater(dbpath, 'pubmed%s' % savetime)
    SaveSearchData(datalist, dbpath)
    txtname="pubmed%s.txt"%savetime
    
    with open(txtname, "w", encoding='utf-8') as file:
        for singleSearchData in datalist:
            output = singleSearchData.to_string()
            output = output + '\n'
            file.write((output))
#








