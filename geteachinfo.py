# -*- coding: utf-8 -*-
import random
import time
from bs4 import BeautifulSoup
import re
import urllib
from timevar import savetime

import sqlite3
def getinfo(PMID):
    #getinfo是用指定的PMID打开文献所在的网页html，爬取一些关键信息，返回成列表或者字典之类的
    baseurl = "https://pubmed.ncbi.nlm.nih.gov/"#baseurl和之前的搜索页面一致
    PMID=str(PMID)
    url=baseurl+PMID
    one_data=[]
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    try:
        response=urllib.request.urlopen(request)
        html=response.read()
        content=BeautifulSoup(html,"html.parser")
        findabs=re.compile(r'<p>.*?([A-Za-z0-9].*[\.\?]).+<\/p>',re.S)
        heading=content.find_all('div',class_="full-view",id="full-view-heading")
        heading=str(heading)#heading是一个包含文章大部分信息的标签
        PMCID=re.search(r'(PMC\d+)\n',heading)  #获取PMCID用于后续的自动下载
        if PMCID ==None:
            PMCID=''
        else:
            PMCID=PMCID.group(1)
        #后面是使用正则提取文章摘要，顺带转换成字符串，然后去除掉多余元素
        abs_key=content.find_all('div',class_="abstract-content selected",id="enc-abstract")
        abs_key=str(abs_key)
        abstract=re.findall(findabs,abs_key)
        if len(abstract)==0:
            abstract=''
        else:
            # print(abstract)
            abstract=re.sub(r'<.+?>','',abstract[0])
            # print(abstract)
            # abstract=re.sub(r'(<strong class="sub-title">).*?(<\/strong>)','',abstract)
        abstract=re.sub(r'\n','',abstract)
        # print(abstract)

        abstract=abstract.replace('strong class="sub-title">','')
        abstract=re.sub(r'\s{3,15}',' ',abstract)
        # print(abstract)
        #后面是提取关键词

        keywords=content.find_all('div',class_="abstract",id="abstract") #keyword和abstract共有一个标签
        # keywords=content.find_all('strong',class_="sub-title")
        # findkeywords=re.compile(r'<strong.*?<\/strong>.*?([A-Za-z0-9].*[\.]).*?<\/p>',re.S)
        findkeywords=re.compile(r'Keywords:.*<\/strong>.*?([A-Za-z0-9].*\.)',re.S)
        keyword=re.search(findkeywords,str(keywords))
        if keyword==None:
            keyword=''
        else:
            keyword=keyword.group(1)
        #这里是在heading中提取归属单位信息affiliations
        findaff=re.compile(r'<sup class="key">\d<\/sup> (.*?)\.<\/li>')
        affiliations=re.findall(findaff,heading)
        if len(affiliations)==0:
            affiliations=''
        else:
            temp2=''
            for i in range(len(affiliations)):
                temp2=temp2+str(i+1)+'. '+affiliations[i]+' '#后面加了一个空格，前面是数字1234.
            affiliations=temp2
        #后面是按顺序添加到临时数据data，用于返回

        one_data.append(PMCID)
        one_data.append(abstract)
        one_data.append(affiliations)
        one_data.append(keyword)
        one_data.append(PMID)
        print(one_data)
        print('获取单页信息成功\n')
        #下面查找作者信息，不找了，直接用搜索页的信息，太费劲了
        # authorlist=content.find_all('span',class_="authors-list-item ")
        # findauthor=re.compile(r'data-ga-label="(.*?)">')
        # author=re.findall(findauthor,str(authorlist))
        # print(author)
        return one_data
    except urllib.error.URLError as e:
        if hasattr(e,"code"):
            print(e.code)
        if hasattr(e,"reason"):
            print(e.reason)
    except(IOError,NameError):
        print("IOError or NameError\n")



# print(getinfo(34794508))

def savedata3(one_data,dbpath):#用于保存单篇文章的几个资料信息，添加到前面构建的sql数据库中
    tablename = 'pubmed%s'%savetime
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    try:
        # for data in one_data:
        #         data='"'+data+'"'
        #         print(data)
        # sql="UPDATE %s SET PMCID = %s,abstract = %s,affiliations = %s,keyword=%s WHERE PMID = %s"
        # val=(tablename,one_data[0],one_data[1],one_data[2],one_data[3],one_data[4])
        cursor.execute("UPDATE %s SET PMCID = ?,abstract = ?,affiliations = ?,keyword=? WHERE PMID = ?"%tablename,
                       (one_data[0], one_data[1], one_data[2], one_data[3], one_data[4]))
        print("单个页面数据写入成功 对应PMID为%s\n"%one_data[4])
    except:
        print("当前页面数据保存失败\n")
    finally:
        conn.commit()
        cursor.close()

def readdata1(dbpath,free): #读取数据库，返回想查询的文献的PMID
    tablename = 'pubmed%s'%savetime
    print(tablename)
    try:
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        try:

            if free==1:
                sql = "SELECT PMCID,doctitle FROM %s WHERE freemark = '2'"%tablename
                # 根据设置的freemark参数，查找数据库文献的信息,free=1用于查找所有免费文献用来下载，而free=2用于拿数据所有文献去获得详细信息
                print(sql)
                cursor.execute(sql)
                print("sql执行成功\n")
                result =cursor.fetchall()
                print(result)
                print('读取sql信息成功 数据类型为PMCID和doctitle\n')
                return result
            elif free==0:
                sql = "SELECT PMID FROM %s"%tablename#查找数据库文献的信息
                cursor.execute(sql)
                result = cursor.fetchall()
                for i in range(len(result)):
                    result[i] = result[i][0]
                print(result)
                print('读取sql信息成功，数据类型为PMID\n')
                return result

        except:
            print("目标数据库读取失败\n")
        finally:
            conn.commit()
            cursor.close()
    except:
        print("连接数据库失败，请检查目标数据库\n")

# if __name__ == "__main__":
def geteachinfo():
    tablename = 'pubmed%s'%savetime
    print('PyCharm\n')
    dbpath = 'pubmedsql'
    result = readdata1(dbpath, 0)
    if result==None:
        print("数据库读取出错，内容为空\n")
    for i in range(len(result)):
        one_data = getinfo(result[i])

        savedata3(one_data, dbpath)
        time.sleep(random.randint(0, 2))




