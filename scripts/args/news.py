from scripts.args.base import BaseArg


class NewsStartFromIndexArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.start_from_index

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--start_from',
                            dest='start_from_index',
                            type=int,
                            nargs='?',
                            default=0,
                            help='index of a news to proceed/start with')
