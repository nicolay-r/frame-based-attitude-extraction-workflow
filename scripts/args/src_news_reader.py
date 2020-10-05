import importlib
from scripts.args.base import BaseArg


class SourceNewsReaderArg(BaseArg):

    Formatter2017 = 'fmt-2017'

    @staticmethod
    def read_argument(args):
        value = args.news_reader
        if value == SourceNewsReaderArg.Formatter2017:
            news_2017_module = importlib.import_module("private.datasets.news_2017")
            return news_2017_module.NewsReader2017Collection(messages_limit=None)

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--news-reader',
                            dest='news_reader',
                            type=str,
                            default=SourceNewsReaderArg.Formatter2017,
                            choices=[SourceNewsReaderArg.Formatter2017],
                            nargs='?',
                            help='News reader/parser.')
