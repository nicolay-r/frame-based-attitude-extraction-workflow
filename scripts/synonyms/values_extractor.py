from core.processing.lemmatization.base import Stemmer
from texts.extraction.default import Default
from texts.extraction.text_parser.base import process_sentence_core_static
from texts.objects.cache.base import BaseObjectCache
from texts.readers.utils import NewsInfo


class TextObjectValuesExtractor:
    """
    Extracts values of objects, recognized by NER models, which is stored in ner_cache
    """

    def __init__(self, ner_cache, stemmer, default_auth_check):
        assert(isinstance(stemmer, Stemmer))

        self.__stemmer = stemmer
        self.__ner_extractor = Default.create_ner_extractor(
            ner=None,
            ner_cache=ner_cache,
            default_auth_check=default_auth_check)

    def iter_for_sentence(self, news_info, s_ind):
        """ Processing title by default
        """
        assert(isinstance(news_info, NewsInfo))

        _, _, objects, _ = process_sentence_core_static(
            news_info=news_info,
            s_ind=s_ind,
            ner_extractor=self.__ner_extractor,
            stemmer=self.__stemmer,
            ner=None,
            frames_helper=None,
            parse_frames=False,
            frames_cache=None,
            using_frames_cache=False,
            need_whole_text_lemmatization=False)

        return objects

    def iter_for_news(self, news_info):
        assert(isinstance(news_info, NewsInfo))

        for obj in self.iter_for_sentence(news_info=news_info, s_ind=BaseObjectCache.TITLE_SENT_IND):
            yield obj

        for s_ind in range(news_info.sentences_count()):
            for obj in self.iter_for_sentence(news_info=news_info, s_ind=s_ind):
                yield obj
