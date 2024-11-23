import argparse
import sys

from timevar import ProjectInfo

"""
This package is argument parser for command line environment.
we point some argument to specify variable and program state

"""


class Argpaser():
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="pubmedsoso is python program for crawler article information and download pdf file",
            usage="python main.py keyword ")

        parser.add_argument('--version', '-v', action='version',
                            version=f'\nCurrent the {ProjectInfo.ProjectName}\n\n version: {ProjectInfo.VersionInfo}\n' +
                                    f'Last updated date: {ProjectInfo.LastUpdate} \n' +
                                    f'Author: {ProjectInfo.AuthorName} \n',
                            help='use --version to show the version')

        ################################################################################################################################
        # --script and --keyword are mutually exclusive. only need one of them.
        
        # parser.add_argument( '-H', "--help", action='help',
        #                     help="Usage:python main.py "
        #                     "--keyword -k specify the keywords to search pubmed\n"
        #                     "add --number or -n to specify the page number you wanna to crawl'\n"
        #                     'add --download_num -d to specify the doc number you wanna to download\n'
        #                      )

        source_group = parser.add_mutually_exclusive_group(required=False)  # True?

        # source_group.add_argument("--script", '-s', action='store_true',
        #                           help='add --script -s arg running script mode',
        #                           default=False)

        parser.add_argument("keyword", type=str,
                                  help='specify the keywords to search pubmed\n For example "headache"')


        parser.add_argument("--page_num", "-n", type=int,
                            help='add --number or -n to specify the page number you wanna to crawl'
                                 'For example --number 10. Default number is 10',
                            default=10)

        parser.add_argument("--download_num", "-d", type=int,
                            help='add --download_num -d to specify the doc number you wanna to download'
                                 'For example -d 10. Default number is 10',
                            default=10)
        #################################################################################################################################

        # parser.add_argument("--debug", '-D', action='store_true',
        #                     help="add -d or --debug args to start debug mode",
        #                     default=False)


        """
        parser.add_argument("--directory", '-d', type=str,
                            help='specify directory to store the output files',
                            default='./document')
                            """

        self.args = parser.parse_args()

if __name__ == "__main__":
    my_argparser = Argpaser()
    args = my_argparser.args
    
    print(args)

