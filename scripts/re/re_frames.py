#!/usr/bin/python
from os import path

from texts.readers.base import BaseNewsReader
from texts.extraction.second.process import FrameDependentTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter


def run_re_by_frames(reader, out_dir, src_dir, settings, start_with_text, parse_frames_in_news_sentences):
    assert(isinstance(reader, BaseNewsReader))
    assert(isinstance(out_dir, str))
    assert(isinstance(settings, Settings))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms,
                                                    display_pn_stat=True)

    contexts_printer = ContextsPrinter(dir=out_dir,
                                       prefix="news_er_")

    tp = FrameDependentTextProcessor(settings=settings,
                                     contexts_printer=contexts_printer,
                                     opinion_statistic_printer=statistic_printer,
                                     parse_frames_in_news_sentences=parse_frames_in_news_sentences,
                                     flag_process_only_titles=True)

    news_it = reader.get_news_iter(src_dir,
                                   desc="FrameBased processor",
                                   start_with_index=start_with_text)

    for text_index, news_info in news_it:
        tp.process_news_and_print(news_info=news_info,
                                  text_index=text_index - start_with_text)

    statistic_printer.save(filepath=path.join(out_dir, "stat.txt"))
