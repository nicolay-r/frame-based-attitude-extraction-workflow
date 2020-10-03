from private.datasets.news_2017 import NewsReader2017Collection
from scripts.args.base import BaseArg


class SourceNewsReaderArg(BaseArg):

    Formatter2017 = 'fmt-2017'

    @staticmethod
    def read_argument(args):
        value = args.news_reader
        if value == SourceNewsReaderArg.Formatter2017:
            return NewsReader2017Collection(messages_limit=None)

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--news-reader',
                            dest='news_reader',
                            type=str,
                            default=SourceNewsReaderArg.Formatter2017,
                            choices=[SourceNewsReaderArg.Formatter2017],
                            nargs='?',
                            help='News reader/parser.')
