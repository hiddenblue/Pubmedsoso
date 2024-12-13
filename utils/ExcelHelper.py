import os
import sqlite3
import sys
from time import sleep

import pandas as pd

from utils.LogHelper import print_error
from config import projConfig
feedbacktime = projConfig.feedbacktime

class ExcelHelper:
    savepath: str = f'./pubmed-{projConfig.savetime}.xlsx'
    tablename: str = f'pubmed{projConfig.savetime}'
    # 原始列名和新列名组成的字典
    rename_dict = {
        'id': '序号',
        'doctitle': '文献标题',
        'full_author': '作者全名',
        'short_author': '作者简名',
        'full_journal': '期刊全名',
        'short_journal': '期刊简名',
        'doi': 'doi',
        'PMID': 'PMID',
        'PMCID': 'PMCID',
        'abstract': '摘要',
        'keyword': '关键词',
        'affiliations': '作者单位',
        'freemark': '是否有免费全文',
        'reviewmark': '是否是review',
        'savepath': '保存路径'
    }

    @classmethod
    def PD_To_excel(cls, dbpath: str, override=False) -> None:
        """
        一个借助pandas对数据导出到excel的更简单的实现
        """
        savepath = cls.savepath
        if os.path.exists(savepath):
            print(f"指定的保存文件 {savepath[2:]} 已存在，文件重复\n\n")
            sleep(feedbacktime)

            if override:
                os.remove(savepath)
            else:
                confirm = input(f"是否删除原有的 {savepath[2:]} 文件, y 或 n\n")
                if confirm.lower() in ("y", "yes"):
                    os.remove(savepath)
                else:
                    print("无法保存成Excel文件，文件名重复冲突\n")
                    sys.exit(-1)
        sleep(feedbacktime)

        """
        id,
        doctitle,
        full_author,
        short_author,
        full_journal,
        short_journal,
        doi,
        PMID,
        PMCID,
        abstract,
        keyword,
        affiliations,
        freemark,
        reviewmark,
        savepath
        """
        try:
            with sqlite3.connect(dbpath) as conn:
                sql: str = f'''
                SELECT
                    id,
                    doctitle,
                    full_author,
                    short_author,
                    full_journal,
                    short_journal,
                    doi,
                    PMID,
                    PMCID,
                    abstract,
                    keyword,
                    affiliations,
                    freemark,
                    reviewmark,
                    savepath
                FROM {cls.tablename}'''
                df = pd.read_sql(sql, conn)

            freemark_column = df['freemark']
            print(freemark_column)
            df.rename(columns=cls.rename_dict, inplace=True)

        except Exception as e:
            print_error("将从数据库当中读取数据时发生错误: ", e)

        try:
            df.to_excel(cls.savepath, sheet_name=cls.tablename, index=False)

        except Exception as e:
            print_error(f"\n爬取数据库信息保存到Excel失败: {e}\n")


if __name__ == "__main__":
    import DBHelper

    dbpath: str = 'pubmedsql'
    table_list: list = DBHelper.DBTableFinder(dbpath)
    if not table_list:
        print("目标数据库不存在或者内容为空，请检查数据库，即将退出")
        sleep(feedbacktime)
        sys.exit(-1)

    print("\n")
    while True:
        sleep(0.5)
        print("当前目录数据库中含有以下table(数据表格)，pubmed后面的数字为生成时精确到秒的时间\n", '----' * 20, '\n')
        for i, table_name in enumerate(table_list, start=1):
            print(f"[{i}] {table_name}")
        print("\n", '----' * 20)
        try:
            x = int(input(
                "\n请输入你想要导出生成Excel表格的数据库table编号，如1,2,3,4，输入0退出程序，注意不要输入上面的pubmedxxxxx编号\n\n"))
            if x == 0:
                print("欢迎使用，程序即将结束")
                sleep(0.5)
                break
            if 1 <= x <= len(table_list):
                index = table_list[x - 1]
                # todo
                savetime = index[6:]
                ExcelHelper.PD_To_excel(dbpath)
                print("此次保存执行完成，下一个循环")
                sleep(3)
                print('----' * 20, "\n")
            else:
                print("输入的编号不在范围内，请重新输入\n")
        except ValueError:
            print_error('----' * 20, '\n')
            print_error("输入错误，如1,2,3,4，输入0退出程序，注意不要输入上面的pubmedxxxxx编号\n\n")
            print_error("重新输入，下一个循环")
            sleep(3)
            print_error('----' * 20, '\n')
    os.system("pause")