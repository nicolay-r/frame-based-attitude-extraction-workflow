from texts.ner_wraps import supported
from scripts.args.base import BaseArg


class NerTypeArg(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.ner_type[0]

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--ner-type',
                            dest='ner_type',
                            type=str,
                            nargs=1,
                            choices=[supported.DEEP_NER_NAME,
                                     supported.ONTONOTES_BERT_MULT_NAME],
                            help='denotes folder (part) in a source')
