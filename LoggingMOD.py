import logging

## 这个模块暂时没有想好用类还是那种全局的get logger的方式

class MyLogger(logging.Logger):
    """
    initialize a log gadge via logging
    """

    def __init__(self, name ,log_level, filename="pubmedsoso.log", disable=False, disable_level=0):
        super().__init__(name)
        self.setLevel(log_level)
        formatter = logging.Formatter(' %(asctime)s - %(levelname)s - %(message)s')

        if filename:
            file_handler = logging.FileHandler(filename)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)

        self.addHandler(console_handler)

        # preserved for log file mode
        # self.logger.basicConfig(filename="pubmedsoso.log", level=log_level, format=' %(asctime)s - %(levelname)s - %(message)s')
        self.info("Start logging")
        self.info("This a message from logger ")



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

    logging.debug('Start of program')


    def factorial(n):
        logging.debug('Start of factorial(%s%%)' % (n))
        total = 1
        for i in range(1, n + 1):
            total *= i
            logging.debug('i is ' + str(i) + ', total is ' + str(total))
        logging.debug('End of factorial(%s%%)' % (n))
        return total


    print(factorial(5))
    logging.debug('End of program')

    logging.basicConfig(filename='myProgram.log', level=logging.DEBUG,
                        format=' %(asctime)s - %(levelname)s - %(message)s')


