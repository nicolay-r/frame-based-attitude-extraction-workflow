import sys


sys.path.append('../../../')

import argparse
from os.path import basename
from core.evaluation.labels import NeutralLabel
from core.helpers.frames import FramesHelper
from core.processing.lemmatization.base import Stemmer
from core.source.frames.complete import FramesCollection, FramePolarity
from texts.readers.base import BaseNewsReader
from scripts.args.src_news_dir import NewsSourceDirArg
from scripts.args.src_news_reader import SourceNewsReaderArg
from scripts.args.news import NewsStartFromIndexArg
from scripts.args.frames import ParseFramesInSentencesArgs
from scripts.args.rusentiframes import RuSentiFramesCacheArgs
from texts.extraction.second.utils import get_frames_polarities
from texts.extraction.default import Default
from texts.frames import TextFrameVariantsCollection
from texts.objects.cache.sqlite_frames_cache import SQLiteFramesCacheData


def is_title_valid(frame_variants_collection, frames):
    assert(isinstance(frame_variants_collection, TextFrameVariantsCollection))

    if len(frame_variants_collection) == 0:
        return False

    polarities, _ = get_frames_polarities(frame_variants_collection, frames)

    neutral = NeutralLabel()

    for pol in polarities:
        assert(isinstance(pol, FramePolarity))

        if pol.Label != neutral:
            # Frame with sentiment polarity existed.
            return True

    return False


def run_frames_cache(reader, stemmer, src_dir, frames, frames_helper, version, start_from_index, miniter_count,
                     parse_frames_in_sentences):
    assert(isinstance(stemmer, Stemmer))
    assert(isinstance(frames, FramesCollection))
    assert(isinstance(reader, BaseNewsReader))
    assert(isinstance(start_from_index, int))
    assert(isinstance(version, str))
    assert(isinstance(frames_helper, FramesHelper))
    assert(isinstance(parse_frames_in_sentences, bool))

    cache = SQLiteFramesCacheData.init_for_rw(frames_helper=frames_helper,
                                              stemmer=stemmer,
                                              rusentiframes_version=version,
                                              parse_sentences=parse_frames_in_sentences,
                                              folder=src_dir)

    with cache:
        for news_index, news_info in reader.get_news_iter(src_dir,
                                                          miniter_count=miniter_count,
                                                          start_with_index=start_from_index):

            cache.register_news(news_info=news_info,
                                process_inner_sentences=parse_frames_in_sentences,
                                is_valid_frames_collection_in_title=lambda fv: len(fv) > 0)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Frames results caching for a particular Source.")

    NewsSourceDirArg.add_argument(parser)
    SourceNewsReaderArg.add_argument(parser)
    NewsStartFromIndexArg.add_argument(parser)
    ParseFramesInSentencesArgs.add_argument(parser)
    RuSentiFramesCacheArgs.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    src_dir = NewsSourceDirArg.read_argument(args)
    reader = SourceNewsReaderArg.read_argument(args)
    frames_filepath = RuSentiFramesCacheArgs.read_argument(args)
    parse_frames_in_sents = ParseFramesInSentencesArgs.read_argument(args)
    start_from_index = NewsStartFromIndexArg.read_argument(args)

    stemmer = Default.create_default_stemmer()
    frames = Default.create_default_frames_collection(frames_filepath)
    f_var = Default.create_default_frame_variants_collection(frames=frames,
                                                             stemmer=stemmer)

    run_frames_cache(reader=reader,
                     src_dir=src_dir,
                     version=basename(frames_filepath),
                     frames=frames,
                     frames_helper=FramesHelper(f_var),
                     stemmer=stemmer,
                     parse_frames_in_sentences=parse_frames_in_sents,
                     start_from_index=start_from_index,
                     miniter_count=2000000)
