import os
from pathlib import Path

from utils import DBHelper

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
                print(f"Deleted {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")


def clean_sqlite(dbpath: str):
    if Path(dbpath).is_file() and Path(dbpath).exists():
        old_table = DBHelper.DBTableFinder(dbpath)

        if old_table:
            for tablename in old_table:
                print(f"Cleaning {tablename}")
                DBHelper.DBRemoveTable(dbpath, tablename)
    else:
        print("there is empty in target db: %s", dbpath)
        return


"""
def run_main_command():
    # 定义主要命令
    command = ['python', 'main.py', 'headache', '-n', '3', '-d', '2']

    # 使用 Popen 来运行命令并实时获取输出
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # 实时读取标准输出和标准错误
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    # 获取剩余的输出
    remaining_output, remaining_error = process.communicate()
    if remaining_output:
        print(remaining_output.strip())
    if remaining_error:
        print(f"Error: {remaining_error.strip()}")
"""

if __name__ == "__main__":
    # 获取当前工作目录
    current_directory = os.getcwd()
    # 清理文件
    clean_files(current_directory)
    # 清理数据库当中的旧表
    clean_sqlite("./pubmedsql")
    # 运行主要命令
    # run_main_command()
