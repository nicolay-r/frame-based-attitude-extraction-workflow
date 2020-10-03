from texts.text_info import NewsSentenceInfo


class BaseObjectCache:
    """
    Base Cache for NER data (API).
    """

    TITLE_SENT_IND = NewsSentenceInfo.TITLE_SENT_IND

    def __init__(self):
        pass

    def is_news_registered(self, news_id):
        raise NotImplementedError()

    def try_get(self, filename, s_ind):
        raise NotImplementedError()
