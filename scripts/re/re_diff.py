#!/usr/bin/python
from os import path

from texts.readers.base import BaseNewsReader
from texts.extraction.diff.process import DiffTextProcessor
from texts.extraction.first import utils
from texts.extraction.first.process import OpinionDependentTextProcessor
from texts.extraction.second.process import FrameDependentTextProcessor
from texts.extraction.settings import Settings
from texts.printing.contexts import ContextsPrinter
from texts.printing.diffcontexts import DiffContextsPrinter
from texts.printing.diffstat import DiffStatisticTitleOpinionsPrinter
from texts.printing.statistics.base import OpinionStatisticBasePrinter


def run_re_diff(reader, pairs_list_filepath, src_dir, out_dir, settings, start_with_text,
                parse_frames_in_news_sentences):
    assert(isinstance(reader, BaseNewsReader))
    assert(isinstance(settings, Settings))
    assert(isinstance(pairs_list_filepath, str))
    assert(isinstance(src_dir, str))
    assert(isinstance(out_dir, str))
    assert(isinstance(parse_frames_in_news_sentences, bool))

    # TODO. Refactor this.
    with open(pairs_list_filepath, 'r') as f:
        opinions = utils.read_opinions(filepath=pairs_list_filepath,
                                       custom_opin_ends_iter=lambda
                                           use_sentiment: OpinionStatisticBasePrinter.iter_opinion_end_values(
                                           f=f, read_sentiment=True),
                                       synonyms=settings.Synonyms)

    statistic_printer = OpinionStatisticBasePrinter(synonyms=settings.Synonyms)

    contexts_printer = ContextsPrinter(dir=out_dir,
                                       prefix="diffstat_er_")

    diffstat_printer = DiffStatisticTitleOpinionsPrinter(filepath=path.join(out_dir, "diffstat.txt"),
                                                         opinions=opinions,
                                                         synonyms=settings.Synonyms)

    diffctx_printer = DiffContextsPrinter(directory=out_dir, filename="diff.txt")
    samectx_printer = DiffContextsPrinter(directory=out_dir, filename="same.txt")

    otp = OpinionDependentTextProcessor(settings=settings,
                                        contexts_printer=contexts_printer,
                                        opinion_statistic_printer=statistic_printer,
                                        expected_opinions=opinions,
                                        parse_frames_in_news_sentences=parse_frames_in_news_sentences)

    ftp = FrameDependentTextProcessor(settings=settings,
                                      contexts_printer=contexts_printer,
                                      opinion_statistic_printer=statistic_printer,
                                      parse_frames_in_news_sentences=parse_frames_in_news_sentences)

    dtp = DiffTextProcessor(opinion_dependent_processor=otp,
                            frame_dependent_processor=ftp,
                            diff_stat=diffstat_printer,
                            diff_ctx=diffctx_printer,
                            same_ctx=samectx_printer)

    for text_index, news_info in reader.get_news_iter(src_dir, start_with_index=start_with_text):
        dtp.process_news(news_info=news_info,
                         text_index=text_index - start_with_text)

    # Printing.
    diffstat_printer.print_statistic()
    statistic_printer.save(filepath=path.join(out_dir, "nonused.txt"))