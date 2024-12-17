import logging
import sys
from time import sleep

from utils.Clean import clean_files, clean_sqlite
from config import projConfig
from utils.LogHelper import medLog

feedbacktime = projConfig.feedbacktime


class MedCli:

    @staticmethod
    def parseLogLevel(level: str):
        if level == "debug":
            return logging.DEBUG
        elif level == "info":
            return logging.INFO
        elif level == "warning":
            return logging.WARNING
        elif level == "error":
            return logging.ERROR
        elif level == "critical":
            return logging.CRITICAL

    @staticmethod
    def SingleArticleMode(**kwargs):

        if 'pmcid' not in kwargs:
            medLog.warning("Single article mode: pmid not found")
            medLog.info("PMID not found, use pmcid instead")

            if 'pmid' in kwargs:
                pmid = kwargs['pmid']
                medLog.info("PMID: %s" % pmid)
            else:
                pass
        else:
            medLog.warning("Single article mode: use pmcid ")
            pmcid = kwargs['pmcid']
            medLog.info("PMCID: %s" % kwargs['pmcid'])
            medLog.info("PMCID: %s" % pmcid)

        medLog.warning("The program is exiting.\n")
        sys.exit(0)

    @staticmethod
    def cleanHistory(directory: str, dbpath: str, **kwargs):

        medLog.warning("The clean.py is up")
        medLog.info("The target directory  is \"%s\"" % directory)
        medLog.info("The target database path is \"%s\"" % dbpath)
        sleep(feedbacktime)

        if kwargs.get('skip', None) is not None and kwargs.get('skip') is True:
            # skip the confirmation process when -Y is enabled
            pass
        else:
            medLog.info("是否要根据以上参数执行清理程序？y or n\n")
            startFlag = input()

            if startFlag not in ['y', 'Y', 'Yes']:
                medLog.critical("程序终止执行\n\n")
                sleep(feedbacktime * 0.5)
                sys.exit()

        # 清理文件
        clean_files(directory)
        # 清理数据库当中的旧表
        clean_sqlite(dbpath)
        # 运行主要命令
        # run_main_command()
        medLog.warning("The clean.py is down")
