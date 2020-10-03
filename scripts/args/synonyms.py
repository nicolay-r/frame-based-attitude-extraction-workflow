from scripts.args.base import BaseArg


class SynonymsCollectionFilepathArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.synonyms_filepath[0]

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--synonyms',
                            dest='synonyms_filepath',
                            nargs=1,
                            help="Synonyms collection filepath")
