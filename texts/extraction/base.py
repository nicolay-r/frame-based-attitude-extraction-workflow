# -*- coding: utf-8 -*-
from core.evaluation.labels import NeutralLabel
from core.runtime.ref_opinon import RefOpinion
from core.source.opinion import OpinionCollection, Opinion
from core.source.synonyms import SynonymsCollection
from texts.extraction.default import Default
from texts.extraction.text_parser.base import process_sentence_core_static
from texts.extraction.settings import Settings
from texts.frames import TextFrameVariantsCollection
from texts.objects.collection import TextObjectsCollection
from texts.readers.utils import NewsInfo
from texts.text_info import NewsSentenceInfo
from texts.printing.contexts import ContextsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter
from texts.printing.statistics.objects import StatisticObjectsPrinter
from texts.printing.utils import ContextDescriptor, TitleDescriptor


class TextProcessor(object):

    base_pref = "[BaseTextProcessor]: "

    OPINIONS_COUNT_CREATED_EP = " Отношений создано"
    OPINIONS_COUNT_SYNONYMOUS_EP = "Число синонимичных отношений"
    OPINIONS_COUNT_TOTAL_EXTRACTED_FROM_TITLES_EP = "Всего извлечено отношений (из заголовков)"
    OPINIONS_COUNT_WITH_MISSED_SYNONYMS_COUNT_EP = "Не найдено синонимов (для объекта либо субъекта)"
    OPINIONS_COUNT_REJECTED_BY_PREPS = "Отвергнуто ввиду наличия предлогов {preps} перед объектами"
    OPINIONS_COUNT_LOOPED_EP = "Число циклических отношений"

    RUSSIAN_PREPS_TO_AVOID_IN_ATTITUDE = ['в', 'на']

    def __init__(self,
                 settings,
                 contexts_printer,
                 opinion_statistic_printer,
                 object_statistic_printer,
                 parse_frames_in_news_sentences):
        assert(isinstance(settings, Settings))
        assert(isinstance(contexts_printer, ContextsPrinter))
        assert(isinstance(parse_frames_in_news_sentences, bool))
        assert(isinstance(opinion_statistic_printer, OpinionStatisticBasePrinter))
        assert(isinstance(object_statistic_printer, StatisticObjectsPrinter) or object_statistic_printer is None)
        self.__settings = settings
        self.__context_printer = contexts_printer
        self.__opinion_statistic_printer = opinion_statistic_printer
        self.__object_statistic_printer = object_statistic_printer
        self.__parse_frames_in_news_sentences = parse_frames_in_news_sentences
        self.__check_obj_preposition_in_title = True

        self.__ner_extractor = Default.create_ner_extractor(
            ner=settings.NER,
            ner_cache=settings.NerCache,
            default_auth_check=settings.default_authorization_check)

        self.__debug_opinions_created = 0
        self.__debug_opinions_with_missed_synonyms = 0
        self.__debug_opinions_looped = 0
        self.__debug_opinions_total_extracted_from_titles = 0
        self.__debug_opinions_rejected_by_preps = 0
        self.__debug_opinions_title_synonymous_existed = 0

    # region properties

    @property
    def Settings(self):
        return self.__settings

    @property
    def _NerExtractor(self):
        return self.__ner_extractor

    @property
    def ContextPrinter(self):
        return self.__context_printer

    @property
    def OpinionStatisticPrinter(self):
        return self.__opinion_statistic_printer

    # endregion

    # region public methods

    def print_contexts(self, title_descriptor, context_descriptors):
        assert(isinstance(title_descriptor, TitleDescriptor))
        assert(isinstance(context_descriptors, list))

        self.ContextPrinter.print_news_title(title_descriptor)
        for cd in context_descriptors:
            self.ContextPrinter.print_extracted_opinion(cd)

    def update_opinions_statistics(self, text_opinions):
        assert(isinstance(text_opinions, OpinionCollection))

        for opinion in text_opinions:
            self.OpinionStatisticPrinter.register_extracted_opinion(opinion)

        self.OpinionStatisticPrinter.clear_extra_parameters()

        # Separator
        self.OpinionStatisticPrinter.add_extra_separator()

        self._add_title_processing_statistics()

        self.OpinionStatisticPrinter.add_extra_parameter(
            description="{pref}{val}".format(pref=self.base_pref,
                                             val=self.OPINIONS_COUNT_CREATED_EP),
            value=str(self.__debug_opinions_created))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.base_pref,
                                             val=self.OPINIONS_COUNT_REJECTED_BY_PREPS.format(preps=self.RUSSIAN_PREPS_TO_AVOID_IN_ATTITUDE)),
            value=str(self.__debug_opinions_rejected_by_preps))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.base_pref,
                                               val=self.OPINIONS_COUNT_WITH_MISSED_SYNONYMS_COUNT_EP),
            value=str(self.__debug_opinions_with_missed_synonyms))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.base_pref,
                                               val=self.OPINIONS_COUNT_LOOPED_EP),
            value=str(self.__debug_opinions_looped))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.base_pref,
                                               val=self.OPINIONS_COUNT_SYNONYMOUS_EP),
            value=str(self.__debug_opinions_title_synonymous_existed))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.base_pref,
                                               val=self.OPINIONS_COUNT_TOTAL_EXTRACTED_FROM_TITLES_EP),
            value=str(self.__debug_opinions_total_extracted_from_titles))

        # Separator
        self.OpinionStatisticPrinter.add_extra_separator()

        self._add_extra_statistic()

        # Separator
        self.OpinionStatisticPrinter.add_extra_separator()

    def process_news_core(self, text_index, news_info):
        raise Exception("Not implemented")

    def decide_label_of_pair_in_title_optional(self, i, j, title_objects, title_frames):
        raise Exception("Not implemented")

    def process_news_content(self, news_info, title_opinions, synonyms):
        """ news_id: assumes a unique name/key
        Perform sentences parsing, excluding news title
        """
        assert(isinstance(news_info, NewsInfo))

        text_opinions = OpinionCollection(opinions=None, synonyms=synonyms)
        cds = []

        for index in range(news_info.sentences_count()):

            _, parsed_sentence, s_objects, s_frames = self._process_sentence_core(news_info, s_ind=index)

            s_opinion_refs, s_opinions_list = self.__extract_sentence_opinion_refs(
                text_objects_collection=s_objects,
                title_opinions=title_opinions,
                synonyms=synonyms)

            if len(s_opinion_refs) == 0:
                continue

            for opinion in s_opinions_list:
                if not text_opinions.has_synonymous_opinion(opinion):
                    add_result = text_opinions.try_add_opinion(opinion)
                    assert(add_result)

            cd = ContextDescriptor(
                sentence_index=index,
                parsed_text=parsed_sentence,
                opinion_refs=s_opinion_refs,
                objects_collection=s_objects,
                text_frames=s_frames,
                frames=self.Settings.Frames)

            cds.append(cd)

        return cds, text_opinions

    def _add_title_processing_statistics(self):
        pass

    def _add_extra_statistic(self):
        pass

    def _extract_opinions_from_title(self, title_terms, title_objects, title_frames, synonyms):
        assert(isinstance(title_terms, list))
        assert(isinstance(title_objects, TextObjectsCollection))
        assert(isinstance(title_frames, TextFrameVariantsCollection))
        assert(isinstance(synonyms, SynonymsCollection))

        opinion_refs = []
        title_opinions = OpinionCollection(opinions=None, synonyms=synonyms)

        TextProcessor.__setup_tags(text_objects_collection=title_objects,
                                   synonyms=synonyms)

        for l_obj in title_objects:
            for r_obj in title_objects:

                l_bound = l_obj.get_bound()
                r_bound = r_obj.get_bound()

                if l_bound.TermIndex == r_bound.TermIndex:
                    continue

                if l_bound.TermIndex >= r_bound.TermIndex:
                    continue

                i = l_obj.CollectionInd
                j = r_obj.CollectionInd

                if not self.__check_auth_correctness(i=i, j=j, objects=title_objects):
                    continue

                label = self.decide_label_of_pair_in_title_optional(
                    i=i, j=j,
                    title_objects=title_objects,
                    title_frames=title_frames)

                if label is None:
                    # Considered by pair-base processor
                    continue

                opinion = Opinion(value_left=l_obj.get_value(),
                                  value_right=r_obj.get_value(),
                                  sentiment=label)

                self.__debug_opinions_created += 1

                if self.__check_obj_preposition_in_title:
                    if self.__reject_by_russian_prepositions(l_obj=l_obj, r_obj=r_obj, title_terms=title_terms):
                        self.__debug_opinions_rejected_by_preps += 1
                        continue

                if not self.__guarantee_synonyms_presence(synonyms=synonyms, obj_value=opinion.value_left):
                    self.__debug_opinions_with_missed_synonyms += 1
                    continue

                if not self.__guarantee_synonyms_presence(synonyms=synonyms, obj_value=opinion.value_right):
                    self.__debug_opinions_with_missed_synonyms += 1
                    continue

                lg_ind = synonyms.get_synonym_group_index(opinion.value_left)
                rg_ind = synonyms.get_synonym_group_index(opinion.value_right)

                if lg_ind == rg_ind:
                    self.__debug_opinions_looped += 1
                    continue

                if not title_opinions.has_synonymous_opinion(opinion):
                    # OK, adding
                    self.__debug_opinions_total_extracted_from_titles += 1
                    add_result = title_opinions.try_add_opinion(opinion)
                    assert(add_result)
                else:
                    self.__debug_opinions_title_synonymous_existed += 1

                opinion_ref = RefOpinion(left_index=i, right_index=j, sentiment=opinion.sentiment)
                opinion_refs.append(opinion_ref)

        return opinion_refs, title_opinions

    def _process_sentence_core(self, news_info, s_ind=NewsSentenceInfo.TITLE_SENT_IND):
        using_frames_cache = self.__settings.FramesCache is not None
        return process_sentence_core_static(
            news_info=news_info,
            s_ind=s_ind,
            stemmer=self.__settings.Stemmer,
            ner=self.__settings.NER,
            ner_extractor=self.__ner_extractor,
            need_whole_text_lemmatization=not using_frames_cache,
            parse_frames_in_news_sentences=self.__parse_frames_in_news_sentences,
            using_frames_cache=using_frames_cache,
            frames_helper=self.__settings.FramesHelper,
            frames_cache=self.__settings.FramesCache)

    # endregion

    # region private methods

    @staticmethod
    def __get_news_id_by_news_info(news_info):
        """ This is how we treat filename, i.e. we consider the latter as id.
        """
        return news_info.FileName

    def __guarantee_synonyms_presence(self, synonyms, obj_value):
        if not synonyms.has_synonym(obj_value):
            if self.__object_statistic_printer is not None:
                self.__object_statistic_printer.register_missed_entity(obj_value)
            return False

        return True

    @staticmethod
    def __check_auth_correctness(i, j, objects):
        i, j = min(i, j), max(i, j)
        while i <= j:
            if not objects.get_object(i).IsAuthorized:
                return False
            i += 1
        return True

    @staticmethod
    def __reject_by_russian_prepositions(l_obj, r_obj, title_terms):
        """
            Если перед объектом стоит предлог «в» или «на» (непосредственно рядом),
            то НЕ СЧИТАТЬ его участником отношения (не субъектом, не объектом)
        """

        prefix_terms = []
        if l_obj.Position > 0:
            prefix_terms.append(title_terms[l_obj.Position - 1].lower())
        if r_obj.Position > 0:
            prefix_terms.append(title_terms[r_obj.Position - 1].lower())

        for prep in TextProcessor.RUSSIAN_PREPS_TO_AVOID_IN_ATTITUDE:
            if prep in prefix_terms:
                return True

        return False

    @staticmethod
    def __extract_sentence_opinion_refs(text_objects_collection, title_opinions, synonyms):
        assert(isinstance(text_objects_collection, TextObjectsCollection))

        opinion_list = []
        opinion_refs = []
        added_opinions = OpinionCollection(opinions=None, synonyms=synonyms)

        TextProcessor.__setup_tags(text_objects_collection=text_objects_collection,
                                   synonyms=synonyms)

        for l_obj in text_objects_collection:
            for r_obj in text_objects_collection:

                if l_obj.CollectionInd == r_obj.CollectionInd:
                    continue

                opinion = Opinion(value_left=l_obj.get_value(),
                                  value_right=r_obj.get_value(),
                                  sentiment=NeutralLabel())

                is_title_already_has_opinion = title_opinions.has_synonymous_opinion(opinion)
                is_already_added = added_opinions.has_synonymous_opinion(opinion)

                is_appropriate = is_title_already_has_opinion and not is_already_added

                if not is_appropriate:
                    continue

                opinion = title_opinions.get_synonymous_opinion(opinion)
                o = RefOpinion(left_index=l_obj.CollectionInd,
                               right_index=r_obj.CollectionInd,
                               sentiment=opinion.sentiment)
                opinion_refs.append(o)

                opinion_list.append(opinion)

                add_result = added_opinions.try_add_opinion(opinion)
                assert(add_result)

        return opinion_refs, opinion_list

    @staticmethod
    def __setup_tags(text_objects_collection, synonyms):
        assert(isinstance(text_objects_collection, TextObjectsCollection))

        for obj in text_objects_collection:

            obj_value = obj.get_value()

            has_obj_synonym = synonyms.has_synonym(obj_value)

            # Setting up tag value.
            if not has_obj_synonym:
                tag = -1
            else:
                tag = synonyms.get_synonym_group_index(obj_value)

            obj.set_tag(tag)

    # endregion
