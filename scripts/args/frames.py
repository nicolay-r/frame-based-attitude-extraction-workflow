from scripts.args.base import BaseArg


class ParseFramesInSentencesArgs(BaseArg):

    @staticmethod
    def read_argument(args):
        return args.parse_frames_in_sents

    @staticmethod
    def add_argument(parser):
        parser.add_argument('--parse-frames-in-sentences',
                            dest='parse_frames_in_sents',
                            action='store_const',
                            const=True,
                            default=False,
                            help='Provide frames parsing for every sentence of a particular news except its title')
