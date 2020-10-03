import io_utils
from os.path import join
from scripts.args.base import BaseArg


class SynonymsCollectionFilepathArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.synonyms_filepath

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--synonyms',
                            dest='synonyms_filepath',
                            nargs='?',
                            default=join(io_utils.get_objects_root(), "synonyms.txt"),
                            help="Synonyms collection filepath")
