#!/usr/bin/python
import collections
from os import path

from io_utils import create_dir
from texts.extraction.pair_based import utils
from texts.extraction.pair_based.process import OpinionDependentTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter


def run_re_by_pairs(news_iter, pairs_list_filepath, out_dir, settings, start_with_text,
                    parse_frames_in_news_sentences):
    assert(isinstance(news_iter, collections.Iterable))
    assert(isinstance(pairs_list_filepath, str))
    assert(isinstance(out_dir, str))
    assert(isinstance(settings, Settings))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    create_dir(out_dir)

    # TODO. Refactor this.
    with open(pairs_list_filepath, 'r') as f:
        opinions = utils.read_opinions(
            filepath=pairs_list_filepath,
            custom_opin_ends_iter=lambda use_sentiment:
            OpinionStatisticBasePrinter.iter_opinion_end_values(f=f, read_sentiment=True),
            synonyms=settings.Synonyms)

    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms)

    contexts_printer = ContextsPrinter(dir=out_dir,
                                       prefix="news_er_")

    tp = OpinionDependentTextProcessor(settings=settings,
                                       contexts_printer=contexts_printer,
                                       opinion_statistic_printer=statistic_printer,
                                       parse_frames_in_news_sentences=parse_frames_in_news_sentences,
                                       expected_opinions=opinions)

    for text_index, news_info in news_iter:
        tp.process_news_and_print(news_info=news_info,
                                  text_index=text_index - start_with_text)

    statistic_printer.save(filepath=path.join(out_dir, "stat.txt"))
