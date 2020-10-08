#!/usr/bin/python
import collections
from os import path
from io_utils import create_dir
from texts.extraction.diff.process import OpinionFilteredTextProcessor
from texts.extraction.pair_based import utils
from texts.extraction.pair_based.process import PairBasedTextProcessor
from texts.extraction.frame_based.process import FrameBasedTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.diffcontexts import DiffContextsPrinter
from texts.printing.diffstat import DiffStatisticTitleOpinionsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter
from texts.printing.statistics.objects import StatisticObjectsPrinter


def run_re_diff(news_iter, pairs_list_filepath, out_dir, settings, parse_frames_in_news_sentences):
    assert(isinstance(news_iter, collections.Iterable))
    assert(isinstance(settings, Settings))
    assert(isinstance(pairs_list_filepath, str))
    assert(isinstance(out_dir, str))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    create_dir(out_dir)

    # TODO. Refactor this.
    with open(pairs_list_filepath, 'r') as f:
        opinions = utils.read_opinions(
            filepath=pairs_list_filepath,
            custom_opin_ends_iter=lambda use_sentiment:
                OpinionStatisticBasePrinter.iter_opinion_end_values(f=f, read_sentiment=True),
            synonyms=settings.Synonyms)

    # Init printers
    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms)
    contexts_printer = ContextsPrinter(dir=out_dir, prefix="diffstat_er_")
    diffstat_printer = DiffStatisticTitleOpinionsPrinter(filepath=path.join(out_dir, "diffstat.txt"),
                                                         opinions=opinions,
                                                         synonyms=settings.Synonyms)
    diffctx_printer = DiffContextsPrinter(directory=out_dir, filename="diff.txt")
    samectx_printer = DiffContextsPrinter(directory=out_dir, filename="same.txt")
    stat_objs_printer = StatisticObjectsPrinter(path.join(out_dir, "objs_stat.txt"))

    pair_based = PairBasedTextProcessor(
        settings=settings,
        contexts_printer=contexts_printer,
        opinion_statistic_printer=statistic_printer,
        expected_opinions=opinions,
        object_statistic_printer=stat_objs_printer,
        parse_frames_in_news_sentences=parse_frames_in_news_sentences)

    frame_based = FrameBasedTextProcessor(settings=settings,
                                          contexts_printer=contexts_printer,
                                          opinion_statistic_printer=statistic_printer,
                                          parse_frames_in_news_sentences=parse_frames_in_news_sentences)

    opinion_filtered = OpinionFilteredTextProcessor(opinion_dependent_processor=pair_based,
                                                    frame_dependent_processor=frame_based,
                                                    diff_stat=diffstat_printer,
                                                    diff_ctx=diffctx_printer,
                                                    same_ctx=samectx_printer)

    for text_index, news_info in news_iter:
        opinion_filtered.process_news(news_info=news_info,
                                      text_index=text_index)

    # Printing.
    diffstat_printer.print_statistic()
    statistic_printer.save(filepath=path.join(out_dir, "nonused.txt"))
    stat_objs_printer.save()
