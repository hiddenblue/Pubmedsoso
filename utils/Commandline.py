import logging
import sys

from utils.LogHelper import medLog


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
