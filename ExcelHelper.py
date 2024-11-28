import os
import sqlite3
import sys
from time import sleep
import xlwt

import DBHelper
from timevar import savetime, feedbacktime

class ExcelHelper:
    savepath: str = f'./pubmed-{savetime}.xls'
    tablename: str = f'pubmed{savetime}'

    @classmethod
    def to_excel(cls, dbpath: str) -> None:
        """
        将数据库输出到Excel文件
        """
        savepath = cls.savepath
        if os.path.exists(savepath):
            print(f"指定的保存文件 {savepath[2:]} 已存在，文件重复\n\n")
            sleep(feedbacktime)
            confirm = input(f"是否删除原有的 {savepath[2:]} 文件, y 或 n\n")
            if confirm.lower() in ("y", "yes"):
                os.remove(savepath)
            else:
                print("无法保存成Excel文件，文件名重复冲突\n")
                sys.exit(-1)
        sleep(feedbacktime)

        try:
            sql: str = f'''
                SELECT
                    id,
                    doctitle,
                    authorlist,
                    journal,
                    doi,
                    PMID,
                    PMCID,
                    abstract,
                    keyword,
                    affiliations,
                    freemark,
                    reviewmark,
                    savepath
                FROM {cls.tablename}
            '''
            db_data: list = DBHelper.DBReader(dbpath, sql)
            print("读取最终数据库信息成功")
        except sqlite3.Error as e:
            print(f"sqlite3 错误: {e}")
            raise
        except Exception as e:
            print(f"读取数据库生成Excel时失败，请检查数据库: {e}")
            raise

        try:
            workbook = xlwt.Workbook(encoding="utf-8", style_compression=0)
            worksheet = workbook.add_sheet("pubmed_soso", cell_overwrite_ok=True)
            headers: tuple = (
                '序号', '文献标题', '作者名单', '期刊年份', 'doi', 'PMID', 'PMCID',
                '摘要', '关键词', '作者单位', '是否有免费全文', '是否是review', '保存路径'
            )

            # 创建表头
            for i, header in enumerate(headers):
                worksheet.write(0, i, header)

            # 填充数据
            for row_idx, row_data in enumerate(db_data, start=1):
                print(f"保存第 {row_idx} 条到Excel")
                row_data = list(row_data)
                for col_idx, value in enumerate(row_data):
                    value = str(value)
                    if col_idx == 10:
                        # freemark 为 '2' 时，“是”有免费的PMC文件PDF
                        value = value.replace('2', '是').replace('1', '否').replace('0', '否')
                    if col_idx == 11:
                        # reviewmark 为 '1' 时，“是”是review类型
                        value = value.replace('1', '是').replace('0', '否')
                    worksheet.write(row_idx, col_idx, value)
            workbook.save(cls.savepath)
            print("\n爬取数据库信息保存到Excel成功\n")
        except Exception as e:
            print(f"\n爬取数据库信息保存到Excel失败: {e}\n")

if __name__ == "__main__":
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
                savetime = index[6:]
                ExcelHelper.to_excel(dbpath)
                print("此次保存执行完成，下一个循环")
                sleep(3)
                print('----' * 20, "\n")
            else:
                print("输入的编号不在范围内，请重新输入\n")
        except ValueError:
            print('----' * 20, '\n')
            print("输入错误，如1,2,3,4，输入0退出程序，注意不要输入上面的pubmedxxxxx编号\n\n")
            print("重新输入，下一个循环")
            sleep(3)
            print('----' * 20, '\n')
    os.system("pause")