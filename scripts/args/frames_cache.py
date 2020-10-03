from scripts.args.base import BaseArg


class FramesCacheDirArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.frames_dir

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--frames-cache-dir',
                            dest='frames_dir',
                            type=str,
                            nargs='?',
                            help='Frames cache directory')
