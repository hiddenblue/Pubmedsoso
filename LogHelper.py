

def print_error(*args, sep=' ', end='\n'):
    # ANSI 转义码用于设置文本颜色为红色
    RED = "\033[91m"
    RESET = "\033[0m"
    # 将所有参数转换为字符串并拼接
    message = sep.join(map(str, args))
    print(f"{RED}{message}{RESET}", end=end)