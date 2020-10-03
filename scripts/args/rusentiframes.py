from os.path import join

import io_utils
from scripts.args.base import BaseArg


class RuSentiFramesCacheArgs(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.frames_filepath

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--rusentiframes',
                            dest='frames_filepath',
                            nargs='?',
                            default=join(io_utils.get_context_root(), "rusentiframes-20.json"),
                            help="Frames collection filepath")
