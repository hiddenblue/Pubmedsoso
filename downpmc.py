# -*- coding: utf-8 -*-
from socket import socket, timeout
import urllib
from urllib import request
import urllib.error
from geteachinfo import readdata1
import sqlite3
import random
import time
import re
import eventlet
import xlwt
from timevar import savetime

#https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9034016/pdf/main.pdf
def downpdf(parameter):
    eventlet.monkey_patch()
    downpara="pmc/articles/"+parameter+"/pdf/main.pdf"
    #openurl是用于使用指定的搜索parameter进行检索，以get的方式获取pubmed的搜索结果页面，返回成html文件
    baseurl = "https://www.ncbi.nlm.nih.gov/"
    url=baseurl+downpara
    timeout_flag=0
    header={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36 Edg/101.0.1210.32"}
    request=urllib.request.Request(url,headers=header)
    html=""
    # try:
    #     response=urllib.request.urlopen(request,timeout=30)
    #     html=response.read()
    #     print("%s.pdf"%parameter,"从目标站获取pdf数据成功")
    #     return html
    try:
        with eventlet.Timeout(180,True):
            response = urllib.request.urlopen(request, timeout=60)
            html = response.read()
            print("%s.pdf" % parameter, "从目标站获取pdf数据成功")
            return html
    except urllib.error.URLError as e:
        if hasattr(e, "code"):  # 判断e这个对象里面是否包含code这个属性
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
        timeout_flag=1
        return timeout_flag
    except eventlet.timeout.Timeout:
        timeout_flag=1
        print("下载目标数据超时")
        return timeout_flag
    except:
        print("%s.pdf"%parameter,"从目标站获取pdf数据失败")

def savepdf(html,PMCID,name,dbpath):
    tablename = 'pubmed%s'%savetime
    # pdf = html.decode("utf-8")  # 使用Unicode8对二进制网页进行解码，直接写入文件就不需要解码了

    try:
        name=re.sub(r'[< > / \\ | : " * ?]',' ',name)
        #需要注意的是文件命名中不能含有以上特殊符号，只能去除掉
        savepath="./document/pub/%s.pdf"%name
        file=open(savepath,'wb')
        print("open success")
        file.write(html)
        file.close()
        # print("%s.pdf"%name,"文件写入到Pubmed/document/pub/下成功")
        print("pdf文件写入成功,文件ID为 %s"%PMCID,"保存路径为Pubmed/document/pub/")
        try:
            conn=sqlite3.connect(dbpath)
            cursor=conn.cursor()
            cursor.execute(" UPDATE %s SET savepath = ? WHERE PMCID =?"%tablename,
                           (savepath,PMCID))
            conn.commit()
            cursor.close()
            return 'success'
            print("pdf文件写入成功,文件ID为 %s"%PMCID,"地址写入到数据库pubmedsql下的table%s中成功"%tablename)
        except:
            print("pdf文件保存路径写入到数据库失败")
    except:
        print("pdf文件写入失败,文件ID为 %s"%PMCID,"文件写入失败,检查路径")

def save2excel(dbpath):
    savepath='./pudmed-%s.xls'%savetime
    tablename = 'pubmed%s' % savetime
    try:
        try:
            conn = sqlite3.connect(dbpath)
            cursor = conn.cursor()
            sql = '''SELECT * FROM %s ''' % tablename
            cursor.execute(sql)
            savedata = cursor.fetchall()
            # print(savedata)
            conn.commit()
            cursor.close()
            print("读取最终数据库信息成功")
        except:
            print("读取数据库生成excel时失败，请检查数据库")
        workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
        worksheet = workbook.add_sheet("pumedsoso", cell_overwrite_ok=True)
        col = (
        '序号', '文献标题', '作者名单', '期刊年份', 'doi', 'PMID', 'PMCID', '摘要', '关键词', '作者单位', '是否有免费全文', '是否是review', '保存路径')
        for i in range(len(col)):
            worksheet.write(0, i, col[i])
        for i in range(len(savedata)):
            print("保存第%d条到excel" % (i + 1))
            savedata[i] = list(savedata[i])
            print(savedata[i])
            for j in range(len(savedata[i])):
                savedata[i][j] = str(savedata[i][j])
                if j == 10:
                    savedata[i][j] = savedata[i][j].replace('2', '是').replace('1', '否').replace('0', '否')
                if j == 11:
                    savedata[i][j] = savedata[i][j].replace('1', '是').replace('0', '否')
                worksheet.write(i + 1, j, savedata[i][j])
        workbook.save(savepath)
        print("\n爬取数据库信息保存到excel成功\n")
    except:
         print("\n爬取数据库信息保存到excel失败\n")


def downpmc(limit):
    tablename = 'pubmed%s'%savetime
    count=0
    dbpath = 'pubmedsql'
    result = readdata1(dbpath, 1)
    for item in result:
        count+=1

        if count > limit:
            print("已达到需要下载的上限，下载停止\n")
            break
        print("开始下载第%d篇"%count)
        #result是从数据库获取的列表元组，其中的每一项构成为PMCID,doctitle
        html=downpdf(item[0])
        if html==None:
            print("网页pdf数据不存在，自动跳过该文献 PMCID为 %s"%item[0])
            continue
        elif html==1:
            print("30s超时,自动跳过该文献 PMCID为 %s"%item[0])
            continue
        status=savepdf(html,item[0],item[1],dbpath)
        if status==None:
            print("保存pdf文件发生错误，自动跳过该文献PMCID为 %s"%item[0])
            continue
        time.sleep(random.randint(0,1))
    save2excel('./pubmedsql')
    print("爬取最终结果信息已经自动保存到excel表格中，文件名为%s"%tablename)
    print("爬取的所有文献已经保存到/document/pub/目录下")
    print("爬取程序已经执行完成，自动退出, 哈哈，no errors no warning")


    # for i in range(len(result)):
    #
    #     time.sleep(random.randint(1,5))
