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
