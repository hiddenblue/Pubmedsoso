import sqlite3
from dataclasses import dataclass

from geteachinfo import SingleDocInfo
from timevar import savetime


# 把一些关于sqlite3相关的操作抽象出来了，方便其他模块调用

@dataclass
class Publication:
    doctitle: str
    title: str
    authorlist: str
    journal: str
    year: str
    doi: str
    pmid: str
    pmcid: str
    abstract: str
    keyword: str
    affiliations: str
    freemark: str
    reviewmark: bool
    savepath: str

    def __repr__(self) -> str:
        return (f"Publication(doctitle='{self.doctitle}', authorlist='{self.authorlist}', "
                f"journal='{self.journal}', doi='{self.doi}', pmid={self.pmid}, pmcid='{self.pmcid}', "
                f"abstract='{self.abstract}', keyword='{self.keyword}', affiliations='{self.affiliations}', "
                f"freemark={self.freemark}, reviewmark={self.reviewmark}, savepath='{self.savepath}')")

    def to_dict(self) -> dict:
        return {
            "doctitle": self.doctitle,
            "authorlist": self.authorlist,
            "journal": self.journal,
            "doi": self.doi,
            "pmid": self.pmid,
            "pmcid": self.pmcid,
            "abstract": self.abstract,
            "keyword": self.keyword,
            "affiliations": self.affiliations,
            "freemark": self.freemark,
            "reviewmark": self.reviewmark,
            "savepath": self.savepath
        }


def DBCreater(dbpath: str) -> bool:
    """
    Creates a new SQLite database file.

    :param dbpath: Path to the SQLite database file.
    """
    try:
        # Connect to the database (this will create the file if it doesn't exist)
        with sqlite3.connect(dbpath) as conn:
            print(f"数据库创建成功: {dbpath}")
            return True
    except sqlite3.Error as e:
        print(f"createDB SQLite Error: {e}\n")
        return False
    except Exception as e:
        print(f"createDB General Error: {e}\n")
        return False


def DBTableCreater(dbpath: str, tablename: str) -> bool:
    """
    Creates a table in the specified SQLite database.

    :param dbpath: Path to the SQLite database file.
    :param tablename: Name of the table to be created.
    """
    # Generate the tablename using the provided savetime
    print(f"tablename: {tablename}")

    # SQL statement to create the table
    sql = f'''
    CREATE TABLE {tablename} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctitle TEXT,
        authorlist TEXT,
        journal TEXT,
        doi TEXT,
        PMID NUMERIC,
        PMCID NUMERIC,
        abstract TEXT,
        keyword TEXT,
        affiliations TEXT,
        freemark NUMERIC,
        reviewmark NUMERIC,
        savepath TEXT
    )
    '''

    try:
        # Connect to the database
        with sqlite3.connect(dbpath) as conn:
            cursor = conn.cursor()
            # Execute the SQL to create the table
            cursor.execute(sql)
            # Commit the transaction
            conn.commit()
            print(f"表 {tablename} 创建成功")
            return True
    except sqlite3.Error as e:
        print(f"createtable SQLite Error: {e}\n")
        return False
    except Exception as e:
        print(f"createtable General Error: {e}\n")
        return False


def DBReader(dbpath: str, sql: str) -> list:
    """
    Reads data from the database using the provided SQL statement.

    :param dbpath: Path to the SQLite database file.
    :param sql: SQL statement to execute (e.g., SELECT).
    :return: List of tuples containing the query results.
    """
    # Generate the tablename using the provided savetime
    tablename = f'pubmed{savetime}'
    print(f"tablename: {tablename}")

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
        print(f"readDB SQLite Error: {e}\n")
    except Exception as e:
        # Handle any other exceptions
        print(f"readDB General Error: {e}\n")
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
            print("Database write operation successful.")
            # Return True if any changes were made, otherwise False
            return conn.total_changes > 0
    except sqlite3.Error as e:
        print(f"writeDB SQLite Error: {e}\n")
    except Exception as e:
        print(f"writeDB General Error: {e}\n")
    finally:
        return False


# 这个函数是用来保存文献打开页面获取到的单独的信息的
def DBSaveInfo(singleinfo: SingleDocInfo, dbpath: str):
    tablename = 'pubmed%s' % savetime

    ret = False
    try:
        # Prepare the data
        pmcid = singleinfo.PMCID
        abstract_str = singleinfo.abstract.to_complete_abs()
        affiliations_str = '\n'.join(singleinfo.affiliations)
        keyword = singleinfo.keyword
        pmid = singleinfo.PMID

        # Execute the update statement
        writer_sql = f"UPDATE {tablename} SET PMCID = ?, abstract = ?, affiliations = ?, keyword = ? WHERE PMID = ?"
        writer_param = (pmcid, abstract_str, affiliations_str, keyword, pmid)

        ret: bool = DBWriter(dbpath, writer_sql, writer_param)
        if ret:
            print(f"单个页面数据写入成功 对应PMID为{pmid}\n")

    except sqlite3.Error as e:
        print(f"当前页面数据保存失败: {e}\n")
    except Exception as e:
        print(f"readDB Error: {e}\n")
