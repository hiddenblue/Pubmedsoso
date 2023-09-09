import argparse

class Argpaser():
    def __init__(self):
        parser = argparse.ArgumentParser(description="pubmedsoso is python program for crawler article infomartion and download pdf file",
                                         usage= "python pubmedsoso --keyword 'alzheimer‘s disease'")

        source_group = parser.add_mutually_exclusive_group(required=True)

        parser.add_argument('--vesrion', '-v', action='version',
                            version=f'Current the {project_name} version: {version} '
                                    f'Last updated date: {last_update} '
                                    f'Author: {author_name} ',
                            help='use --version to show the version')

        source_group.add_argument("--script", '-s', action='store_true',
                            help='add --script -s arg running script mode',
                            default=False)

        source_group.add_argument("--keyword", '-k', type=str,
                            help='specity the keywords to search pubmed\n For example --keyword "alzheimer‘s disease"')

        parser.add_argument("--debug", '-D', action='store_true',
                            help="add -d or --debug args to start debug mode",
                            default=False)

        parser.add_argument("--directory", '-d', type=str,
                            help='specify directory to store the output files',
                            default='./')

        parser.add_argument("--name", '-n', type=str,
                            help='add --name or -n to specify global file for pubmedsoso\n'
                                 ' For example --name mypubmedsoso. Default name is pubmedsoso',
                            default='pubmedsoso')

        parser.add_argument("--ban_excel", '-b', action='store_false',
                            help='add this args to stop excel output'
                                 'For example --ban_excel.',
                            default=False)


        self.args = parser.parse_args()

        # parser.add_argument("--keyword", '-k', type=str,
        #                     help="specity the keywords to search pubmed\n For example --keyword alzheimer‘s disease",
        #                 )

        # parser.add_argument("--script", '-s', action='store_true',
        #                     help='add --script -s arg running script mode',
        #                     default=False)

if __name__ == "__main__":

    version = '2.0.1'
    project_name = 'pubmedsoso'
    last_update = '2023-09-10'
    author_name = 'hiddenblue'

    my_argparser = Argpaser()

    print(my_argparser.args.__dict__)
