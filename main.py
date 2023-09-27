from argparser import Argpaser
from pubmedsoso import Pubmedsoso


if __name__ == "__main__":
  #  version = '2.0.1'
  # project_name = 'pubmedsoso'
  # last_update = '2023-09-10'
  # author_name = 'hiddenblue'

    command_arg = Argpaser().args
    pubmedsoso = Pubmedsoso(command_arg)
    pubmedsoso.spider_loop()





