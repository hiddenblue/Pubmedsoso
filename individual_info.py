# -*- coding: utf-8 -*-

import random
import re
import sqlite3
import time
from LoggingMOD import MyLogger
import logging
logger = MyLogger("Myapp", logging.DEBUG)

import requests

from timevar import savetime


if __name__ == "__main__":

    dbpath = "./pubmedsql"
    tablename = "pubmed20230805204820"
    with create_sql_conn(dbpath) as cursor:
        logging.info(f"connect to to target database:{dbpath}success!")
        sql = """SELECT PMID from pubmed20230806220632"""
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
        except sqlite3.OperationalError as e:
            logger.error(f"Error when execute sql command: {e}")
            exit(-1)
    print(result)



