import typing
import logging
from LoggingDemo import MyLogger
logger = MyLogger("Myapp", logging.DEBUG)
from time import sleep
import yaml
import pydantic

class BaseInit:
    """ 文件初始化的基类，方便继承复用代码。
    """

    def __init__(self, config_file_path):
        """

        :param config_file_path: 给定的pubmedsoso config.yaml 参数的地址。
        """
        self.config_yaml = self.read_config_file(config_file_path)
        ### 引入了一个自定义的配置文件类型
        self.config = Config()

        # 全局参数初始化，太多就不挨个初始化了，全整进去得了
        try:
            for key,values in self.config_yaml['global_params']:
                self.config.key = values
        except KeyError as e:
            logging.error(f'unable to load the global params from config path: {config_file_path}, error: {e}')
            logging.error(f'the program will exit soon')
            exit(-1)

        # command 模式专用参数
        try:
            for key,values in self.config_yaml['command_mode_args']:
                self.config.key = values
        except KeyError as e:
            logging.error(f'unable to load the command params from config path: {config_file_path}, error: {e}')
            logging.error(f'the program will exit soon')
            exit(-1)
        """
        the default format of global_params in config_path

        global_params:
            is_debug: False
            sql_path: "."
            excel_path: "."
            doc_down_path: "./document/pub"
            default_name: "pubmedsql"
            excel_output: true
            log_output: true
        """

    # the defalult config file path is "./config.yaml"
    def read_config_file(self, config_file_path)->dict:
        try:
            with open(config_file_path, "r", encoding="utf-8") as fd:  # file descriptor
                config = fd.read()
            return yaml.load(config, Loader=yaml.FullLoader)

        except FileNotFoundError:
            print(f"unable to find the config_path :{config_file_path} file, No such file or directory.")

        except IOError:
            print(f"IO error, unable to read the config_path :{config_file_path} file.")

class ScriptInit(BaseInit):
    """通过给定配置文件参数可以返回一个Config类型的配置文件对象，继承自base_init
    """
    def __init__(self, config_file_path):

        ## 在BaseInit的基础上我加上了script模式特有的config_file_path
        super(BaseInit, self).__init__(config_file_path)
        try:
            if self.config_yaml['exec_mode'] == 'script':
                self.config.exec_mode = self.config_yaml['exec_mode']
                self.config.page_num = self.config_yaml['scipt_mode_args']['page_num']  # 默认下载文献信息的页数
                self.config.download_num = self.config_yaml['scipt_mode_args']['download_num']  # 默认只下载一篇文献PDF
                self.config.search_keywords = self.config_yaml['scipt_mode_args'][
                    'search_keywords']  # 这里我们可能要考虑多组关键词的情况 我们就用list格式，暂时不支持单独设置他们的参数
        except KeyError as e:
            logger.error(f'Config() __init__ ERROR: {e}, chek your config yaml file')
            exit(-1)

class ArgsInit(BaseInit):
    """
    通过继承了BaseInit的属性，加上了Args特有的属性即可。
    """
    def __init__(self, command_args, config_file_path):
        super(BaseInit, self).__init__(config_file_path)
        try:
            if command_args.script:
                for key, values in command_args.items():
                    self.config.key= values
        except KeyError as e:
            logging.error(f'ArgsInit error: {e}')
            exit(-1)

class CMDInit(BaseInit):
    """
    这部分需要后期完成了，先闲置
    """
    def __init__(self, config_file_path):
        super(BaseInit, self).__init__(config_file_path)
        while(True):
            self.config.keyword = str(input("请在下面粘贴你构建的搜索结果的parameter\n"))

            if self.config.keyword == '':
                print("输入有误\n")
                continue
            page_num =input("即将爬取所有文献的信息，请输入你想爬取信息的页数(每页50个）\n")
            sleep(1)
            try:
                page_num = int(page_num)
            except (ValueError, TypeError) as e:
                print(e)
                print("输入有误\n")
                continue
            self.config.pagenum = page_num
            sleep(1)

            download_num =input("请输入你想下载的文献的数量\n")
            sleep(1)
            try:
                download_num = int(download_num)
            except (ValueError, TypeError) as e:
                print(e)
                print("输入有误\n")
                continue
            self.config.download_num = download_num
            sleep(1)

class Config:
    """
    一个专门为这个程序设计的配置文件数据结构
    增减后期功能和对应的数据结构
    """
    def __init__(self):
        pass

    @property
    def keyword(self):
        return self.keyword

    @keyword.setter
    def keyword(self, keyword):
        self.keyword = keyword

    @keyword.deleter
    def keyword(self):
        raise RuntimeError('can not delete keyword')
##########################################################
    @property
    def pagenum(self):
        return self.pagenum

    @pagenum.setter
    def pagenum(self, pagenum):
        self.pagenum = pagenum

    @pagenum.deleter
    def pagenum(self):
        raise RuntimeError('can not delete pagenum')

    ##########################################################
    @property
    def download_num(self):
        return self.download_num

    @download_num.setter
    def download_num(self, download_num):
        self.download_num = download_num

    @download_num.deleter
    def download_num(self):
        raise RuntimeError('can not delete download_num')

    ##########################################################
    @property
    def is_debug(self):
        return self.is_debug

    @is_debug.setter
    def is_debug(self, is_debug):
        self.is_debug = is_debug

    @is_debug.deleter
    def is_debug(self):
        raise RuntimeError('can not delete is_debug')

    ##########################################################
    @property
    def default_name(self):
        return self.default_name

    @default_name.setter
    def default_name(self, default_name):
        self.default_name = default_name

    @default_name.deleter
    def default_name(self):
        raise RuntimeError('can not delete default_name')

    ##########################################################
    @property
    def output_path(self):
        return self.output_path

    @output_path.setter
    def output_path(self, output_path):
        self.output_path = output_path

    @output_path.deleter
    def output_path(self):
        raise RuntimeError('can not delete output_path')
    ##########################################################
    @property
    def excel_output(self)-> bool:
        return self.excel_output

    @excel_output.setter
    def excel_output(self, excel_output):
        self.excel_output = excel_output

    @excel_output.deleter
    def excel_output(self):
        raise RuntimeError('can not delete excel_output')

##########################################################

    @property
    def exec_mode(self)-> bool:
        return self.exec_mode

    @exec_mode.setter
    def exec_mode(self, exec_mode):
        self.exec_mode = exec_mode

    @exec_mode.deleter
    def exec_mode(self):
        raise RuntimeError('can not delete exec_mode')
    ##########################################################

    @property
    def test_arg(self)-> bool:
        return self.test_arg

    @test_arg.setter
    def test_arg(self, test_arg):
        self.test_arg = test_arg

    @test_arg.deleter
    def test_arg(self):
        raise RuntimeError('can not delete test_arg')
    ##########################################################