from scripts.args.base import BaseArg


class NerCacheFilepathArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.ner_cache_filepath[0]

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--ner-cache-filepath',
                            dest='ner_cache_filepath',
                            type=str,
                            nargs=1,
                            help='NER cache filepath')
