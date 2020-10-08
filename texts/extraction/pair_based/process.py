# -*- coding: utf-8 -*-
from core.evaluation.labels import NeutralLabel
from core.source.opinion import OpinionCollection, Opinion
from texts.readers.utils import NewsInfo
from texts.extraction.base import TextProcessor
from texts.extraction.parsed_news_utils import to_input_terms
from texts.frames import TextFrameVariantsCollection
from texts.objects.collection import TextObjectsCollection
from texts.text_info import NewsSentenceInfo
from texts.printing.utils import TitleDescriptor


class OpinionDependentTextProcessor(TextProcessor):

    pref = "[OpinionDependentProcessor]: "

    DOCUMENTS_PARSED_EP = "Разобрано документов"
    SENTENCES_PARSED_EP = "Разобрано предложений"

    def __init__(self,
                 settings,
                 expected_opinions,
                 contexts_printer,
                 opinion_statistic_printer,
                 parse_frames_in_news_sentences,
                 object_statistic_printer=None):
        assert(isinstance(expected_opinions, OpinionCollection))
        super(OpinionDependentTextProcessor, self).__init__(
            settings=settings,
            contexts_printer=contexts_printer,
            parse_frames_in_news_sentences=parse_frames_in_news_sentences,
            opinion_statistic_printer=opinion_statistic_printer,
            object_statistic_printer=object_statistic_printer)

        self.__expected_opinions = expected_opinions
        self.__debug_docs_parsed = 0
        self.__debug_sentences_parsed = 0

    # region public methods

    def process_news(self, text_index, news_info):
        return self.process_news_core(text_index=text_index,
                                      news_info=news_info)

    def process_news_and_print(self, text_index, news_info):

        processed_result = self.process_news_core(text_index=text_index,
                                                  news_info=news_info)

        self.__debug_docs_parsed += 1
        self.__debug_sentences_parsed += len(news_info)

        if processed_result is None:
            return None

        td, cds, title_opinions, text_opinions = processed_result

        if len(title_opinions) == 0:
            return None

        self.print_contexts(title_descriptor=td, context_descriptors=cds)
        self.update_opinions_statistics(text_opinions)

    def process_news_core(self, text_index, news_info):
        assert(isinstance(text_index, int))
        assert(isinstance(news_info, NewsInfo))

        if len(news_info) == 0:
            return None

        title_terms, parsed_title, title_objects, title_frames = self._process_sentence_core(news_info)

        title_opinion_refs, title_opinions = self._extract_opinions_from_title(title_terms=title_terms,
                                                                               title_objects=title_objects,
                                                                               title_frames=title_frames,
                                                                               synonyms=self.Settings.Synonyms)

        if len(title_opinions) == 0:
            return None

        td = TitleDescriptor(news_info=news_info,
                             parsed_title=parsed_title,
                             text_index=text_index,
                             title_frames=title_frames,
                             opinion_refs=title_opinion_refs,
                             objects_collection=title_objects,
                             frames=self.Settings.Frames)

        # process news contents.
        cds, text_opinions = self.process_news_content(news_info=news_info,
                                                       title_opinions=title_opinions,
                                                       synonyms=self.Settings.Synonyms)

        return td, cds, title_opinions, text_opinions

    def decide_label_of_pair_in_title_optional(self, i, j, title_objects, title_frames):
        l_obj = title_objects.get_object(i)
        r_obj = title_objects.get_object(j)

        opinion = Opinion(value_left=l_obj.get_value(),
                          value_right=r_obj.get_value(),
                          sentiment=NeutralLabel())

        if not self.__expected_opinions.has_synonymous_opinion(opinion):
            return None

        return self.__expected_opinions.get_synonymous_opinion(opinion).sentiment

    # endregion

    # region protected methods

    def _add_extra_statistic(self):
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="{pref}{val}".format(pref=self.pref, val=self.DOCUMENTS_PARSED_EP),
            value=str(self.__debug_docs_parsed))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="{pref}{val}".format(pref=self.pref, val=self.SENTENCES_PARSED_EP),
            value=str(self.__debug_sentences_parsed))

    # endregion