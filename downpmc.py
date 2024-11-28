# -*- coding: utf-8 -*-
import random
import re
import sqlite3
import time

import xlwt

from geteachinfo import readdata1, TempPMID
from timevar import savetime
from PDFHelper import PDFHelper

def save2excel(dbpath):
    savepath = './pudmed-%s.xls' % savetime
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
            '序号', '文献标题', '作者名单', '期刊年份', 'doi', 'PMID', 'PMCID', '摘要', '关键词', '作者单位',
            '是否有免费全文', '是否是review', '保存路径')
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
    tablename = 'pubmed%s' % savetime
    count = 0
    dbpath = 'pubmedsql'
    PMID_list: [TempPMID] = readdata1(dbpath)

    PMCID_list = [item for item in PMID_list if item.PMCID != None]
    for item in PMCID_list:
        count += 1

        if count > limit:
            print("已达到需要下载的上限，下载停止\n")
            break
        print("开始下载第%d篇" % count)
        # result是从数据库获取的列表元组，其中的每一项构成为PMCID,doctitle
        html = PDFHelper.PDFdownload(item.PMCID)
        if html == None:
            print("网页pdf数据不存在，自动跳过该文献 PMCID为 %s" % item.PMCID)
            continue
        elif html == 1:
            print("30s超时,自动跳过该文献 PMCID为 %s" % item.PMCID)
            continue
        status = PDFHelper.PDFSave(html, item.PMCID, item.doctitle, dbpath)
        if status == None:
            print("保存pdf文件发生错误，自动跳过该文献PMCID为 %s" % item.PMCID)
            continue
        time.sleep(random.randint(0, 1))
    save2excel(dbpath)  # 这里我把默认的数据库路径改成了全局变量dbpath
    print("爬取最终结果信息已经自动保存到excel表格中，文件名为%s" % tablename)
    print("爬取的所有文献已经保存到/document/pub/目录下")
    print("爬取程序已经执行完成，自动退出, 哈哈，no errors no warning")

    # for i in range(len(result)):
    #
    #     time.sleep(random.randint(1,5))
