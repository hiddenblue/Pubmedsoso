import os
from pathlib import Path

from utils import DBHelper
from utils.LogHelper import medLog

"""
这个模块是用来清理当前目录下的之前执行的历史文件的
比如xlsx文件和sqlite数据库当中的表
如果不是有清理的需要，请勿执行，执行会丢失所有的历史记录（已下载pdf除外）

"""

def clean_files(directory):
    # 遍历目录中的所有文件
    for filename in os.listdir(directory):
        # 检查文件是否为Excel文件或文本文件
        if filename.endswith(('.xls', 'xlsx')) or filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                medLog.warning(f"Deleted {file_path}")
            except Exception as e:
                medLog.error(f"Error deleting {file_path}: {e}")


def clean_sqlite(dbpath: str):
    medLog.warning(f"the {os.path.basename(__file__)}: will clean sqlite table")
    if Path(dbpath).is_file() and Path(dbpath).exists():
        old_table = DBHelper.DBTableFinder(dbpath)

        if old_table:
            for tablename in old_table:
                if tablename.startswith('pubmed'):
                    medLog.warning(f"Cleaning {tablename}")
                    DBHelper.DBRemoveTable(dbpath, tablename)
    else:
        medLog.warning("there is empty in target db: %s", dbpath)
        return

# 具体的执行逻辑搬运到commandline.py当中去了


if __name__ == "__main__":
    print(os.path.basename(__file__))
