#!/usr/bin/python
import collections
from os import path
from io_utils import create_dir
from texts.extraction.frame_based.process import FrameDependentTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter


def run_re_by_frames(news_iter, out_dir, settings, parse_frames_in_news_sentences):
    assert(isinstance(news_iter, collections.Iterable))
    assert(isinstance(out_dir, str))
    assert(isinstance(settings, Settings))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    create_dir(out_dir)

    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms,
                                                    display_pn_stat=True)

    contexts_printer = ContextsPrinter(dir=out_dir,
                                       prefix="news_er_")

    tp = FrameDependentTextProcessor(settings=settings,
                                     contexts_printer=contexts_printer,
                                     opinion_statistic_printer=statistic_printer,
                                     parse_frames_in_news_sentences=parse_frames_in_news_sentences,
                                     flag_process_only_titles=True)

    for text_index, news_info in news_iter:
        tp.process_news_and_print(news_info=news_info,
                                  text_index=text_index)

    statistic_printer.save(filepath=path.join(out_dir, "stat.txt"))
