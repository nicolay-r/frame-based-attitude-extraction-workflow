from scripts.args.base import BaseArg


class OptionalOutputDirArg(BaseArg):
    """ Optional parameter
     """

    @staticmethod
    def read_argument(args):
        return args.output_dir

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--output-dir',
                            dest='output_dir',
                            type=str,
                            nargs='?',
                            help='Output directory')


class OutputDirArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.output_dir[0]

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--output-dir',
                            dest='output_dir',
                            type=str,
                            nargs=1,
                            help='Output directory')
