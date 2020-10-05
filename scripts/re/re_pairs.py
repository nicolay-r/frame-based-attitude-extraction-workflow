#!/usr/bin/python
from os import path
from texts.readers.base import BaseNewsReader
from texts.extraction.pair_based import utils
from texts.extraction.pair_based.process import OpinionDependentTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter


def run_re_by_pairs(reader, pairs_list_filepath, src_dir, out_dir, settings, start_with_text,
                    parse_frames_in_news_sentences):
    assert(isinstance(reader, BaseNewsReader))
    assert(isinstance(pairs_list_filepath, str))
    assert(isinstance(src_dir, str))
    assert(isinstance(out_dir, str))
    assert(isinstance(settings, Settings))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    # TODO. Refactor this.
    # TODO. Update reading.
    opinions = utils.read_opinions(filepath=pairs_list_filepath,
                                   synonyms=settings.Synonyms)

    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms)

    contexts_printer = ContextsPrinter(dir=out_dir,
                                       prefix="news_er_")

    tp = OpinionDependentTextProcessor(settings=settings,
                                       contexts_printer=contexts_printer,
                                       opinion_statistic_printer=statistic_printer,
                                       parse_frames_in_news_sentences=parse_frames_in_news_sentences,
                                       expected_opinions=opinions)

    news_it = reader.get_news_iter(src_dir,
                                   desc="Pair-based processor",
                                   start_with_index=start_with_text)

    for text_index, news_info in news_it:
        tp.process_news_and_print(news_info=news_info,
                                  text_index=text_index - start_with_text)

    statistic_printer.save(filepath=path.join(out_dir, "stat.txt"))
