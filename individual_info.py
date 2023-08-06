# -*- coding: utf-8 -*-

import random
import re
import sqlite3
import time
import logging

import requests
from bs4 import BeautifulSoup

from timevar import savetime


class Logging:
    """自定义的一个logging类，方便在各个模块之间共享"""
    def __init__(self, log_filename= "pubmedsoso.log"):
        self.logging = logging
        self.logging.basicConfig(filename=log_filename,
                            format="%(asctime)s-%(name)s-%(levelname)s-%(message)s - %(funcName)s",
                            level=logging.INFO)


class ArticleDetail:
    """单个文献的详细信息, 都是str type用于储存信息的格式"""

    def __init__(self, doctitle="", author_list="", journal="", doi="", PMID="",
                 PMCID= "", abstract="", keyword="", affiliations="", is_review="",
                 full_text_type="", save_path="" ):

        self.doctitle = doctitle
        self.authorlist = author_list
        self.journal = journal
        self.doi = doi
        self.PMID = PMID
        self.PMCID = PMCID
        self.abstract = abstract
        self.keyword = keyword
        self.affiliations = affiliations
        self.is_review = is_review
        self.full_text_type = full_text_type
        self.savepath = save_path

class create_sql_conn:
    """手动构建一个适用于sqlite3的上下文管理器，方便后面多次打开和关闭sqlite3数据库
    在打开返回cursor，然后在退出的时候自动关闭。"""

    def __init__(self, dbpath: str):
        self.conn = sqlite3.connect(dbpath)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        """这里会被as xxx:调用，返回sql的cursor"""

        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文管理器的时候需要，然后close cursor，最后关闭连接"""
        self.conn.commit()
        self.conn.close()
        return False

if __name__ == "__main__":
    text_log = Logging()
    text_log.logging.info(msg="日志系统测试")

    dbpath = "./pubmedsql"
    tablename = "pubmed20230805204820"
    with create_sql_conn(dbpath) as cursor:
        logging.info(f"connect to to target database:{dbpath}success!")
        sql = """SELECT PMID from pubmed20230806220632"""
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except sqlite3.OperationalError as e:
            text_log.logging.error(f"Error when execute sql command: {e}")
            exit(-1)
    print(result)



