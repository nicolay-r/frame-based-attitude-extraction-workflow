from scripts.args.base import BaseArg


class NewsSourceDirArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.source_dir

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--source-dir',
                            dest='source_dir',
                            type=str,
                            nargs='?',
                            help='Source directory')
