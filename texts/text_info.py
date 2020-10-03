class NewsSentenceInfo:

    TITLE_SENT_IND = -1

    def __init__(self, news_id, sent_id):
        self.__news_id = news_id
        self.__sent_id = sent_id

    @property
    def IsTitle(self):
        return self.__sent_id == -1

    @property
    def NewsIndex(self):
        return self.__news_id

    @property
    def SentenceIndex(self):
        return self.__sent_id

    @classmethod
    def create_for_title(cls, news_id):
        return cls(news_id=news_id,
                   sent_id=cls.TITLE_SENT_IND)

    @classmethod
    def register_sentence(cls, news_id, sent_ind):
        assert (sent_ind > 0)
        return cls(news_id=news_id,
                   sent_id=sent_ind)
