# -*- coding: utf-8 -*-
from core.evaluation.labels import Label
from texts.readers.utils import NewsInfo
from texts.extraction.base import TextProcessor
from texts.extraction.parsed_news_utils import to_input_terms
from texts.extraction.frame_based.limits import NerTypesLimitation
from texts.extraction.frame_based.utils import get_frames_polarities, mean
from texts.frames import TextFrameVariantsCollection
from texts.objects.collection import TextObjectsCollection
from texts.text_info import NewsSentenceInfo
from texts.printing.utils import TitleDescriptor
from texts.utils import optional_invert_label


class FrameDependentTextProcessor(TextProcessor):

    pref = "[FrameProcessor]: "

    ATTITUDES_COUNT_CHECKED_EP = "Число отношений проанализировано"

    ATTITUDES_COUNT_WITH_NON_VALID_OBJ_TYPES_EP = \
        "Число отношений в которых один из объектов вне множества {group}"

    OPINIONS_COUNT_APPLIED_FOR_PROCESSING_BY_FRAMES_EP = \
        "Число отношений, принятых на обработку фреймами"
    OPINIONS_COUNT_WITHOUT_FRAMES_INSIDE_EP = \
        "Число отношений без фреймов внутри"
    OPINIONS_COUNT_WITHOUT_POLARITY_FRAMES_EP = \
        "Число отношений в которых есть фреймы без полярности"
    OPINIONS_COUNT_WITH_UNKNOWN_LABEL_EP = \
        "Число отношений в которых не удалось определить метку"
    OPINIONS_COUNT_VALID_EP = \
        "Число отношений прошедших проверку"

    def __init__(self,
                 settings,
                 contexts_printer,
                 opinion_statistic_printer,
                 parse_frames_in_news_sentences,
                 object_statistic_printer=None,
                 flag_process_only_titles=False):
        assert(isinstance(flag_process_only_titles, bool))

        super(FrameDependentTextProcessor, self).__init__(
            settings=settings,
            contexts_printer=contexts_printer,
            opinion_statistic_printer=opinion_statistic_printer,
            parse_frames_in_news_sentences=parse_frames_in_news_sentences,
            object_statistic_printer=object_statistic_printer)

        self.__debug_title_opinions_checked = 0
        self.__debug_title_opinions_with_empty_frames = 0
        self.__debug_title_opinions_with_unknown_label = 0
        self.__debug_title_opinions_with_polarities_missed = 0
        self.__debug_title_opinions_with_objs_non_valid_by_type = 0
        self.__debug_title_opinions_processed_by_frames = 0

        self.__debug_valid = 0
        self.__process_only_titles = flag_process_only_titles
        self.__ner_types_limitation = NerTypesLimitation(settings.NERClassType)

    # region public methods

    def process_news(self, text_index, news_info):
        return self.process_news_core(text_index=text_index,
                                      news_info=news_info)

    def process_news_and_print(self, text_index, news_info):

        processed_result = self.process_news_core(text_index=text_index,
                                                  news_info=news_info)

        if processed_result is None:
            return

        td, cds, title_opinions, text_opinions = processed_result
        if len(title_opinions) == 0:
            return None

        self.print_contexts(title_descriptor=td,
                            context_descriptors=[] if self.__process_only_titles else cds)
        self.update_opinions_statistics(title_opinions if self.__process_only_titles else text_opinions)

    def process_news_core(self, text_index, news_info):
        assert(isinstance(text_index, int))
        assert(isinstance(news_info, NewsInfo))

        if len(news_info) == 0:
            return None

        title_terms, parsed_title, title_objects, title_frames = self._process_sentence_core(news_info)

        if len(title_frames) == 0:
            return None

        if len(title_objects) == 0:
            return None

        title_opinion_refs, title_opinions = self._extract_opinions_from_title(
            title_terms=title_terms,
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

        if self.__process_only_titles:
            return td, None, title_opinions, None

        cds, text_opinions = self.process_news_content(
            news_info=news_info,
            title_opinions=title_opinions,
            synonyms=self.Settings.Synonyms)

        return td, cds, title_opinions, text_opinions

    def decide_label_of_pair_in_title_optional(self, i, j, title_objects, title_frames):

        self.__debug_title_opinions_checked += 1

        # Checking left object.
        l_obj = title_objects.get_object(i)
        if not self.__ner_types_limitation.is_valid_obj(l_obj):
            self.__debug_title_opinions_with_objs_non_valid_by_type += 1
            return None

        # Checking right object.
        r_obj = title_objects.get_object(j)
        if not self.__ner_types_limitation.is_valid_obj(r_obj):
            self.__debug_title_opinions_with_objs_non_valid_by_type += 1
            return None

        # Getting object bounds
        l_bound = l_obj.get_bound()
        r_bound = r_obj.get_bound()

        frame_variants_in = self.__get_frames_within(left_in=l_bound.TermIndex + l_bound.Length,
                                                     right_in=r_bound.TermIndex - 1,
                                                     text_frame_variants=title_frames)

        text_polarities, is_inverted = get_frames_polarities(text_frame_variants=frame_variants_in,
                                                             frames=self.Settings.Frames)

        self.__debug_title_opinions_processed_by_frames += 1

        if len(frame_variants_in) == 0:
            self.__debug_title_opinions_with_empty_frames += 1
            return None

        if len(frame_variants_in) != len(text_polarities):
            self.__debug_title_opinions_with_polarities_missed += 1
            return None

        labels = [optional_invert_label(p.Label, is_inverted[p_index]).to_int()
                  for p_index, p in enumerate(text_polarities)]

        label = mean(labels)

        # Force to negative if there is a negative example
        if -1 in labels:
            label = -1

        if -1 < label < 1:
            self.__debug_title_opinions_with_unknown_label += 1
            return None

        self.__debug_valid += 1

        return Label.from_int(int(label))

    # endregion

    # region protected methods

    def _add_title_processing_statistics(self):
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="{pref}{val}".format(pref=self.pref,
                                             val=self.ATTITUDES_COUNT_CHECKED_EP),
            value=str(self.__debug_title_opinions_checked))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.pref,
                                               val=self.ATTITUDES_COUNT_WITH_NON_VALID_OBJ_TYPES_EP.format(
                                                   group=self.__ner_types_limitation.SupportedNerTypesSet)),
            value=str(self.__debug_title_opinions_with_objs_non_valid_by_type))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t{pref}{val}".format(pref=self.pref,
                                               val=self.OPINIONS_COUNT_APPLIED_FOR_PROCESSING_BY_FRAMES_EP),
            value=str(self.__debug_title_opinions_processed_by_frames))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t\t{pref}{val}".format(pref=self.pref,
                                                 val=self.OPINIONS_COUNT_WITHOUT_FRAMES_INSIDE_EP),
            value=str(self.__debug_title_opinions_with_empty_frames))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t\t{pref}{val}".format(pref=self.pref,
                                                 val=self.OPINIONS_COUNT_WITHOUT_POLARITY_FRAMES_EP),
            value=str(self.__debug_title_opinions_with_polarities_missed))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t\t{pref}{val}".format(pref=self.pref,
                                                 val=self.OPINIONS_COUNT_WITH_UNKNOWN_LABEL_EP),
            value=str(self.__debug_title_opinions_with_unknown_label))
        self.OpinionStatisticPrinter.add_extra_parameter(
            description="\t\t{pref}{val}".format(pref=self.pref,
                                                 val=self.OPINIONS_COUNT_VALID_EP),
            value=str(self.__debug_valid))

    # endregion

    # region private methods

    @staticmethod
    def __get_frames_within(left_in, right_in, text_frame_variants):
        assert(isinstance(text_frame_variants, TextFrameVariantsCollection))
        frames_in = []
        for frame in text_frame_variants:
            if left_in <= frame.Position <= right_in:
                frames_in.append(frame)
        return frames_in

    # endregion
