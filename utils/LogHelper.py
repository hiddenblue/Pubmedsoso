import logging
import sys

from colorlog import ColoredFormatter


def print_error(*args, sep=' ', end='\n'):
    # ANSI 转义码用于设置文本颜色为红色
    RED = "\033[91m"
    RESET = "\033[0m"
    # 将所有参数转换为字符串并拼接
    message = sep.join(map(str, args))
    print(f"{RED}{message}{RESET}", end=end)


class MedLogger:

    def __init__(self, terminalLogLevel=logging.DEBUG, log_file="app.log", FileLogLevel=logging.INFO):
        # 创建一个日志记录器
        self.logger = logging.getLogger("Pubmed")
        self.logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

        # 创建一个控制台处理器，将日志输出到终端
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(terminalLogLevel)  # 设置控制台日志级别

        # 创建一个文件处理器，将日志输出到文件
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setLevel(FileLogLevel)  # 设置文件日志级别

        # 创建日志格式化器
        # 创建颜色格式化器
        color_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s-%(name)s-%(levelname)s- %(message)s",
            datefmt="%H:%M:%S",  # 简化的日期格式（仅时间）
            log_colors={
                'DEBUG': 'white',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )

        file_formatter = logging.Formatter("%(asctime)s-%(name)s-%(levelname)s- %(message)s")

        # 将格式化器添加到处理器
        console_handler.setFormatter(color_formatter)
        file_handler.setFormatter(file_formatter)

        # 将处理器添加到日志记录器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    @property
    def terminalLogLevel(self):
        return self.logger.handlers[0].level

    @property
    def fileLogLevel(self):
        return self.logger.handlers[1].level

    @staticmethod
    def setTerminalLogLevel(logger: logging.Logger, level):
        logger.handlers[0].setLevel(level)

    @staticmethod
    def setFileLogLevel(logger: logging.Logger, level):
        logger.handlers[1].setLevel(level)


# 这里生成一个全局的日志模块
medLog = MedLogger().logger

# 测试日志输出
if __name__ == "__main__":
    # medLog.setLevel(logging.WARNING)
    MedLogger.setTerminalLogLevel(medLog, logging.ERROR)

    medLog.debug("这是一个 DEBUG 级别的日志")
    medLog.info("这是一个 INFO 级别的日志")
    medLog.warning("这是一个 WARNING 级别的日志")
    medLog.error("这是一个 ERROR 级别的日志")
    medLog.critical("这是一个 CRITICAL 级别的日志")

    MedLogger.setTerminalLogLevel(medLog, logging.DEBUG)

    medLog.debug("这是一个 DEBUG 级别的日志1")
    medLog.info("这是一个 INFO 级别的日志1")
    medLog.warning("这是一个 WARNING 级别的日志1")
    medLog.error("这是一个 ERROR 级别的日志1")
    medLog.critical("这是一个 CRITICAL 级别的日志1")

    doctitle: str = "hello"
    medLog.debug("doctitle: ", doctitle)

    PMCID = "PMCID"

    medLog.error("PMCID: %s" % PMCID,
                 "从目标站获取pdf数据失败")
