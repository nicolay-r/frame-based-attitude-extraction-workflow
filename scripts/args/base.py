class BaseArg:

    @staticmethod
    def read_argument(parser):
        raise NotImplementedError()

    @staticmethod
    def add_argument(parser):
        raise NotImplementedError()
