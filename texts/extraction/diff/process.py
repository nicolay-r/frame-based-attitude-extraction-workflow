# -*- coding: utf-8 -*-
from core.runtime.ref_opinon import RefOpinion
from core.source.opinion import OpinionCollection, Opinion
from texts.extraction.pair_based.process import PairBasedTextProcessor
from texts.extraction.frame_based.process import FrameBasedTextProcessor
from texts.objects.collection import TextObjectsCollection
from texts.printing.diffcontexts import DiffContextsPrinter
from texts.printing.diffstat import DiffStatisticTitleOpinionsPrinter
from texts.printing.utils import ContextDescriptor


class OpinionFilteredTextProcessor:

    __bool_list = [True, False]

    def __init__(self,
                 opinion_dependent_processor,
                 frame_dependent_processor,
                 diff_stat,
                 diff_ctx,
                 same_ctx):
        assert(isinstance(opinion_dependent_processor, PairBasedTextProcessor))
        assert(isinstance(frame_dependent_processor, FrameBasedTextProcessor))
        assert(isinstance(diff_stat, DiffStatisticTitleOpinionsPrinter))
        assert(isinstance(diff_ctx, DiffContextsPrinter))
        assert(isinstance(same_ctx, DiffContextsPrinter))
        self.__frame_processor = frame_dependent_processor
        self.__opinion_processor = opinion_dependent_processor
        self.__diff_stat = diff_stat
        self.__diff_ctx = diff_ctx
        self.__same_ctx = same_ctx
        self.__debug_comparison_missed = 0

    def process_news(self, text_index, news_info):

        frame_result = self.__frame_processor.process_news(text_index=text_index,
                                                           news_info=news_info)

        if frame_result is None:
            return

        pair_result = self.__opinion_processor.process_news(text_index=text_index,
                                                            news_info=news_info)

        if pair_result is None:
            return

        pair_td, pair_cds, pair_title_opinions, pair_text_opinions = pair_result
        frame_td, frame_cds, frame_title_opinions, frame_text_opinions = frame_result

        assert(len(pair_title_opinions) >= len(pair_text_opinions))
        assert(len(frame_title_opinions) >= len(frame_text_opinions))

        has_match = False
        for opinion in frame_title_opinions:
            if pair_title_opinions.has_synonymous_opinion(opinion):
                has_match = self.__diff_stat.try_register_title_opinion_from_other_method(opinion)
                if not has_match:
                    self.__debug_comparison_missed += 1
            else:
                self.__debug_comparison_missed += 1

        if not has_match:
            return

        # Title
        temp_refs = frame_td.opinion_refs
        for is_same in self.__bool_list:

            frame_td.opinion_refs = self.__filter_opinion_refs(
                pair_opinions=pair_title_opinions,
                frame_opinion_refs=temp_refs,
                objects_collection=frame_td.objects_collection,
                is_same=is_same)

            if len(frame_td.opinion_refs) == 0:
                continue

            ctx = self.__same_ctx if is_same else self.__diff_ctx
            ctx.print_title(frame_td)

        for cd in frame_cds:
            assert(isinstance(cd, ContextDescriptor))

            # Context
            temp_refs = cd.opinion_refs
            for is_same in self.__bool_list:

                cd.opinion_refs = self.__filter_opinion_refs(
                    pair_opinions=pair_text_opinions,
                    frame_opinion_refs=temp_refs,
                    objects_collection=cd.objects_collection,
                    is_same=is_same)

                if len(cd.opinion_refs) == 0:
                    continue

                ctx = self.__same_ctx if is_same else self.__diff_ctx
                ctx.print_context(cd)

        self.__diff_stat.update_texts_parsed_count(text_index)
        self.__diff_stat.clear_extra_parameters()
        self.__diff_stat.add_extra_parameter(
            description="Число не сопоставленных отношений (есть по второму, но не найденых по первому критерию)",
            value=self.__debug_comparison_missed)

    def __filter_opinion_refs(self, pair_opinions, frame_opinion_refs, objects_collection, is_same):

        def same(ref_opinion):
            return self.__check_ref_opin_in_collection(ref_opinion=ref_opinion,
                                                       opinions=pair_opinions,
                                                       text_objects=objects_collection,
                                                       is_same=is_same)

        return list(filter(same, frame_opinion_refs))

    def __check_ref_opin_in_collection(self, ref_opinion, opinions, text_objects, is_same):
        assert(isinstance(ref_opinion, RefOpinion))
        assert(isinstance(opinions, OpinionCollection))
        assert(isinstance(text_objects, TextObjectsCollection))
        assert(isinstance(is_same, bool))

        l_obj = text_objects.get_object(ref_opinion.LeftIndex)
        r_obj = text_objects.get_object(ref_opinion.RightIndex)

        o = Opinion(value_left=l_obj.get_value(),
                    value_right=r_obj.get_value(),
                    sentiment=ref_opinion.Sentiment)

        if opinions.has_synonymous_opinion(o):
            o_existed = opinions.get_synonymous_opinion(o)
            return (o_existed.sentiment != o.sentiment and not is_same) or\
                   (o_existed.sentiment == o.sentiment and is_same)

        return False
