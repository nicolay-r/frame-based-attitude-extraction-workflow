from core.evaluation.labels import Label
from core.source.opinion import Opinion


class StatisticSentimentElement:

    def __init__(self, opinion):
        assert(isinstance(opinion, Opinion))
        self.__opinion = opinion
        self.__pos = 0
        self.__neg = 0

    # region properties

    @property
    def Opinion(self):
        return self.__opinion

    @property
    def Count(self):
        return self.__pos + self.__neg

    @property
    def PositiveCount(self):
        return self.__pos

    @property
    def NegativeCount(self):
        return self.__neg

    # endregion

    def inc(self, label, count):
        assert(isinstance(label, Label))
        assert(isinstance(count, int) and count >= 1)

        if label.to_int() == 1:
            self.__pos += count
        elif label.to_int() == -1:
            self.__neg += count
        else:
            raise Exception("Label is not supported within related element: {}".format(label.to_int()))

