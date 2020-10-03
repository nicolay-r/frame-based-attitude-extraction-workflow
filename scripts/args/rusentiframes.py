from scripts.args.base import BaseArg


class RuSentiFramesCacheArgs(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.frames_filepath[0]

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--rusentiframes',
                            dest='frames_filepath',
                            nargs=1,
                            help="Frames collection filepath")
