# -*- coding: utf-8 -*-
from time import sleep
import typing

from pathlib import Path
from argparser import Argpaser
from LoggingMOD import MyLogger
import logging
logger = MyLogger("Myapp", logging.DEBUG)

from ConfigManage import Config, ScriptInit, ArgsInit, CMDInit
from init import DIRinit, SQLInit, Search_param
from GetInfo import get_info,data_sweep
from sql import save_info_sql, read_any_sql

class Pubmedsoso():

    def __init__(self, command_args:dict, config_file_path="./config.yaml"):

        ## we can initialize the pubmedsoso by three ways: script/command input/args/
        logger.info(f"start config managment mod")
        logger.debug(f"config_file_path: {config_file_path} , command_args: {command_args}")
        if command_args.keyword:
            logger.info("使用命令行参数配置本项目")
            print(command_args)
            arg_init = ArgsInit(command_args=command_args, config_file_path=config_file_path)
            self.config = arg_init.config

        elif command_args.script:
            logger.info("使用配置文件参数配置本项目")
            print(command_args)
            print(command_args.script)
            script_init = ScriptInit(config_file_path)
            self.config = script_init.config
        else:
            logger.info("使用cmd交换界面输入参数配置本项目")
            print(command_args)
            cmd_init = CMDInit(config_file_path)
            self.config = cmd_init.config

        logger.debug(f"command args:{command_args}")
        logger.debug(self.config.__dict__)
        logger.info("config manage mod initialize correctly!")
        logger.info("start Directory and SQlite3 initiation soon")


        DIRinit(self.config.output_path)
        logger.info("Dir init run correctly")
        logger.debug(f"config.output_path='{self.config.output_path}'")


        SQLInit(self.config.output_path)
        logger.info("SQL init run correctly")
        logger.debug(f"config.output_path='{self.config.output_path}'")

        logger.info("initialize finished. The spider will start soon.")

    def spider_loop(self)->list:

        logger.info("spieder loop will start ")

        search_param = Search_param(self.config.keyword)
        search_param.size = 50
        search_param.specify_any_param('format','abstract')

        result_num = None
        all_result = []
        max_page = None

        for i in range(1, self.config.page_num + 1):
            if max_page and i > max_page: # we check loop condition here
                break

            search_param.page = i

            logger.debug(f"spider search param: '{search_param.search_dict}'")
            direct_link = search_param.url
            logger.debug(f'spdier direct_link: "{direct_link}"')
            multi_result, result_num = get_info(direct_link)   # receive target data and result_num
            clean_result = data_sweep(multi_result)

            all_result.append(clean_result)

            if not result_num:  # calculate for the first time when result_num = None
                max_page = int(result_num / search_param.size) + 1
        # here we save the result info to sqlite3 DB
        save_info_sql(all_result, self.config.output_path)
        return all_result

    def download_pdf(self):
        PMCID_list = read_any_sql(self.config.output_path, 'PMCID name')








if __name__ == "__main__":
    # config_path = "./config.yaml"   ## pubmedsoso配置文件的位置，默认和main.py在同一个文件夹下
    # pubmedsoso = PubmedSoSo(config_path)
    #
    dbpath = "./pubmedsql"
    # main()
    # ?term=cell%2Bblood&filter=datesearch.y_1&size=20

    search_param = Search_param("alzheimer's disease")
    search_param.size = 50
    search_param.specify_any_param('sort', "jour")
    print(search_param.gen_search_param())