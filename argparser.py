import argparse
from timevar import version_info

"""
This package is argument parser for command line environment.
we point some argument to sepcify variable and program state

"""
class Argpaser():
    def __init__(self):
        parser = argparse.ArgumentParser(description="pubmedsoso is python program for crawler article infomartion and download pdf file",
                                         usage= "python pubmedsoso --keyword 'alzheimer‘s disease'")

        parser.add_argument('--vesrion', '-v', action='version',
                            version=f'Current the {version_info.get("project_name")} version: {version_info.get("project_name")} '
                                    f'Last updated date: {version_info.get("last_update")} '
                                    f'Author: {version_info.get("author_name")} ',
                            help='use --version to show the version')

        ################################################################################################################################
        # --scirpt and --keyword are multually exclusvie. only need one of them.

        source_group = parser.add_mutually_exclusive_group(required=False)  # True?

        source_group.add_argument("--script", '-s', action='store_true',
                            help='add --script -s arg running script mode',
                            default=False)

        source_group.add_argument("--keyword", '-k', type=str,
                            help='specity the keywords to search pubmed\n For example --keyword "alzheimer‘s disease"')

        #################################################################################################################################

        parser.add_argument("--debug", '-D', action='store_true',
                            help="add -d or --debug args to start debug mode",
                            default=False)

        parser.add_argument("--directory", '-d', type=str,
                            help='specify directory to store the output files',
                            default='./document')

        parser.add_argument("--name", '-N', type=str,
                            help='add --name or -N to specify global file for pubmedsoso\n'
                                 ' For example --name mypubmedsoso. Default name is pubmedsoso',
                            default='pubmedsoso')

        parser.add_argument("--ban_excel", '-b', action='store_false',
                            help='add this args to stop excel output'
                                 'For example --ban_excel.',
                            default=False)

        parser.add_argument("--page_num", "-n", type=int,
                            help='add --number or -n to specify the page number you wanna to crawl'
                            'For example --number 10. Defalut number is 10',
                            default=10)


        self.args = parser.parse_args()

        # parser.add_argument("--keyword", '-k', type=str,
        #                     help="specity the keywords to search pubmed\n For example --keyword alzheimer‘s disease",
        #                 )

        # parser.add_argument("--script", '-s', action='store_true',
        #                     help='add --script -s arg running script mode',
        #                     default=False)

if __name__ == "__main__":

    my_argparser = Argpaser()

    print(my_argparser.args.__dict__)
