import pathlib
import sqlite3
from typing import List, Union

from config import projConfig
from utils.DataType import Publication
from utils.DataType import SingleDocInfo, TempPMID
from utils.LogHelper import medLog


# 把一些关于sqlite3相关的操作抽象出来了，方便其他模块调用


def DBCreater(dbpath: str) -> bool:
    """
    Creates a new SQLite database file.

    :param dbpath: Path to the SQLite database file.
    """
    if not pathlib.Path(dbpath).exists():
        medLog.warning("target database path does not exist. Program will create it.")

    try:
        # Connect to the database (this will create the file if it doesn't exist)
        with sqlite3.connect(dbpath) as conn:
            medLog.info(f"数据库连接成功: {dbpath}")
            return True
    except sqlite3.Error as e:
        medLog.error(f"createDB SQLite Error: {e}\n")
        return False
    except Exception as e:
        medLog.error(f"createDB General Error: {e}\n")
        return False


def DBTableCreater(dbpath: str, tablename: str) -> bool:
    """
    Creates a table in the specified SQLite database.

    :param dbpath: Path to the SQLite database file.
    :param tablename: Name of the table to be created.
    """
    # Generate the tablename using the provided savetime
    medLog.info(f"tablename: {tablename}")

    # SQL statement to create the table
    sql = f'''
    CREATE TABLE {tablename} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctitle TEXT,
        full_author TEXT,
        short_author TEXT,
        full_journal TEXT,
        short_journal TEXT,
        doi TEXT,
        PMID TEXT,
        PMCID TEXT,
        abstract TEXT,
        keyword TEXT,
        affiliations TEXT,
        freemark TEXT,
        reviewmark NUMERIC,
        savepath TEXT
    )'''

    try:
        # Connect to the database
        with sqlite3.connect(dbpath) as conn:
            cursor = conn.cursor()
            # Execute the SQL to create the table
            cursor.execute(sql)
            # Commit the transaction
            conn.commit()
            medLog.info(f"表 {tablename} 创建成功")
            return True
    except sqlite3.Error as e:
        medLog.error(f"createtable SQLite Error: {e}\n")
        return False
    except Exception as e:
        medLog.error(f"createtable General Error: {e}\n")
        return False


def DBTableFinder(dbpath: str) -> list[str]:
    try:
        readSql = "SELECT name from sqlite_master where type='table' and name like 'pubmed%' order by name"
        tablelist = DBReader(dbpath, readSql)
        for i in range(len(tablelist)):
            tablelist[i] = tablelist[i][0]
        return tablelist

    except sqlite3.Error as e:
        medLog.error("sqlite3 error: %s\n" % e)

    except Exception as e:
        medLog.error("数据库查询出错，请检查数据库: %s" % e)


def DBRemoveTable(dbpath: str, tablename: str) -> bool:
    try:
        current_table = DBTableFinder(dbpath)

        if tablename not in current_table:
            medLog.info(f"the target table: {tablename} is not exist")
            return False

        remove_sql = f"DROP TABLE {tablename}"
        DBWriter(dbpath, remove_sql)
        return True

    except Exception as e:
        medLog.error(f"removeTable SQLite Error: {e}\n")
        return False


def DBReader(dbpath: str, sql: str) -> list:
    """
    Reads data from the database using the provided SQL statement.

    :param dbpath: Path to the SQLite database file.
    :param sql: SQL statement to execute (e.g., SELECT).
    :return: List of tuples containing the query results.
    """

    # Initialize an empty list to store the results
    ret = []

    try:
        # Connect to the database using a context manager to ensure it closes automatically
        with sqlite3.connect(dbpath) as conn:
            # Create a cursor object to execute SQL commands
            cursor = conn.cursor()
            # Execute the provided SQL query
            cursor.execute(sql)
            # Fetch all results from the executed query
            ret = cursor.fetchall()
    except sqlite3.Error as e:
        # Handle SQLite-specific errors
        medLog.error(f"readDB SQLite Error: {e}\n")
    except Exception as e:
        # Handle any other exceptions
        medLog.error(f"readDB General Error: {e}\n")
    finally:
        # Return the fetched results
        return ret


def DBWriter(dbpath: str, sql: str, params: tuple = None) -> bool:
    """
    Writes data to the database using the provided SQL statement.

    :param dbpath: Path to the SQLite database file.
    :param sql: SQL statement to execute (e.g., INSERT, UPDATE, DELETE).
    :param params: Tuple of parameters to use with the SQL statement (optional).
    :return: Boolean indicating whether any changes were made.
    """
    try:
        with sqlite3.connect(dbpath) as conn:
            cursor = conn.cursor()
            # Execute the query with parameters if provided
            if params is not None:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            # Commit the transaction
            conn.commit()
            medLog.info("Database write operation successful.")
            # Return True if any changes were made, otherwise False
            return conn.total_changes > 0
    except sqlite3.Error as e:
        medLog.error(f"writeDB SQLite Error: {e}\n")
    except Exception as e:
        medLog.error(f"writeDB General Error: {e}\n")
    finally:
        return False


# 这个函数是用来保存文献打开页面获取到的单独的信息的
def DBSaveInfo(singleinfo: SingleDocInfo, dbpath: str):
    tablename = 'pubmed%s' % projConfig.savetime

    ret = False
    try:
        # Prepare the data
        pmcid = singleinfo.PMCID
        doi = singleinfo.doi
        abstract_str = singleinfo.abstract.to_complete_abs()
        affiliations_str = '\n'.join(singleinfo.affiliations)
        keyword = singleinfo.keyword
        pmid = singleinfo.PMID

        # Execute the update statement
        writer_sql = f"UPDATE {tablename} SET PMCID = ?, doi = ?, abstract = ?, affiliations = ?, keyword = ? WHERE PMID = ?"
        writer_param = (pmcid, doi, abstract_str, affiliations_str, keyword, pmid)

        ret: bool = DBWriter(dbpath, writer_sql, writer_param)
        if ret:
            medLog.info(f"单个页面数据写入成功 对应PMID为{pmid}\n")

    except sqlite3.Error as e:
        medLog.error(f"当前页面数据保存失败: {e}\n")
    except Exception as e:
        medLog.error(f"readDB Error: {e}\n")


def DBFetchAllFreePMC(dbpath: str, tableName) -> list[TempPMID]:
    """
    相当于一个重载的 DBFetchAllPMID 函数，只返回了有pmc原文的部分

    
    """
    ret = DBFetchAllPMID(dbpath, tableName)

    return [temppmid for temppmid in ret if temppmid.PMCID is not None]


def DBFetchAllPMID(dbpath: str, tableName) -> list[TempPMID]:
    """
    虽然说这个函数叫FetchPMID
    但是实际上返回的是PMID PMCID doctitle合成的TempPMID数据类型
    请注意使用
    
    """
    medLog.info("dbpath: %s" % dbpath)
    medLog.info("tablename: %s" % tableName)

    try:
        sql = "SELECT PMCID, PMID, doctitle FROM %s" % tableName

        if len(sql) < 200:
            medLog.debug(sql)
        else:
            medLog.debug(sql[:200])

        ret = DBReader(dbpath, sql)
        for i in range(len(ret)):
            ret[i] = TempPMID(ret[i][0], ret[i][1], ret[i][2])
        medLog.debug(ret)
        medLog.info('读取sql信息成功 数据类型为PMCID和doctitle\n')
        return ret

    except Exception as e:
        medLog.error("连接数据库失败，请检查目标数据库: %s\n" % e)
        return []


def DBFetchAllRecord(dbpath: str, tableName, outputpublication=True) -> Union[List[Publication], List, None]:
    """
    虽然说这个函数叫FetchPMID
    但是实际上返回的是PMID PMCID doctitle合成的TempPMID数据类型
    请注意使用
    
    """
    medLog.info("dbpath: %s " % dbpath)
    medLog.info("tablename: %s" % tableName)

    try:
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
                FROM {tableName}
            '''  # 根据设置的freemark参数，查找数据库文献的信息,free = 1用于查找所有免费文献用来下载，而free = 2用于拿数据所有文献去获得详细信息
        medLog.info(sql)
        ret = DBReader(dbpath, sql)

        if outputpublication == False:
            medLog.debug(ret)
            medLog.info('读取sql信息成功 数据类型为Publication\n')
            return ret

        for i in range(len(ret)):
            ret[i] = Publication(ret[i][0], ret[i][1], ret[i][2],
                                 ret[i][3], ret[i][4], ret[i][5],
                                 ret[i][6], ret[i][7], ret[i][8],
                                 ret[i][9], ret[i][10], ret[i][11],
                                 ret[i][12], ret[i][13])
        medLog.debug(ret)
        medLog.info('读取sql信息成功 数据类型为Publication\n')
        return ret

    except Exception as e:
        medLog.info("连接数据库失败，请检查目标数据库: %s\n" % e)
        return None
