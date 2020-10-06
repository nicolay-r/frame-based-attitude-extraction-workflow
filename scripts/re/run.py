import os
import sys
import argparse
from os import mkdir
from os.path import join, basename, exists

sys.path.append('../../')

import io_utils

from texts.objects.cache.sqlite_frames_cache import SQLiteFramesCacheData
from texts.extraction.settings import Settings
from texts.objects.cache.sqlite_ner_cache import SQLiteNERCacheData

from scripts.args.frames_cache import FramesCacheDirArg
from scripts.args.news import NewsStartFromIndexArg
from scripts.args.out_dir import OutputDirArg
from scripts.args.src_news_dir import NewsSourceDirArg
from scripts.args.src_news_reader import SourceNewsReaderArg
from scripts.args.synonyms import SynonymsCollectionFilepathArg
from scripts.args.frames import ParseFramesInSentencesArgs
from scripts.args.ner_cache import NerCacheFilepathArg
from scripts.args.ner_type import NerTypeArg
from scripts.args.rusentiframes import RuSentiFramesCacheArgs
from scripts.re.re_frames import run_re_by_frames
from scripts.re.re_diff import run_re_diff
from scripts.re.re_pairs import run_re_by_pairs


def get_task_name(task_index, prefix, ner_name):
    return "{t_ind}-{src_folder}-{ner_name}".format(
        t_ind=str(task_index),
        src_folder=prefix,
        ner_name=ner_name)


TASK_EXTRACTION_BY_PAIRS = "ext_by_pairs"
TASK_EXTRACTION_BY_FRAMES = "ext_by_frames"
TASK_DIFF_EXTRACTION = "ext_diff"


task_to_index = {
    TASK_EXTRACTION_BY_PAIRS: 1,
    TASK_EXTRACTION_BY_FRAMES: 2,
    TASK_DIFF_EXTRACTION: 3
}


def get_output_root_task_new_part_folder(out_dir, task_name):
    assert(isinstance(out_dir, str))
    assert(isinstance(task_name, str))

    for part_index in range(100):

        folder = os.path.join(out_dir, "{task_name}-P{part}/".format(
            task_name=str(task_name),
            part=str(part_index).zfill(3)))

        if os.path.exists(folder):
            continue

        io_utils.create_dir(folder)

        return folder


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Relation extraction from news_2017 collection")

    parser.add_argument('--task',
                        dest='task',
                        type=str,
                        nargs=1,
                        choices=[TASK_DIFF_EXTRACTION,
                                 TASK_EXTRACTION_BY_FRAMES,
                                 TASK_EXTRACTION_BY_PAIRS],
                        default=False,
                        help='Utilize object authorization')

    parser.add_argument('--use-auth-list',
                        dest='use_auth_list',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Utilize object authorization by using a list with authorized values')

    parser.add_argument('--diff-pairs-list',
                        dest='pairs_list_filepath',
                        nargs='?',
                        help="[<{tasks}> only] Pairs list filepath".format(
                            tasks=",".join([TASK_DIFF_EXTRACTION, TASK_EXTRACTION_BY_PAIRS])))

    parser.add_argument('--restore_missed_objects',
                        dest='restore_missed_objects',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Restore, missed Named Entity Recognition, objects (using authorized objects list)')

    parser.add_argument('--use-ner-cache-only',
                        dest='use_ner_cache',
                        action='store_const',
                        const=True,
                        default=False,
                        help='Obtaining information about objects only from cache')

    SynonymsCollectionFilepathArg.add_argument(parser)
    OutputDirArg.add_argument(parser)
    NewsSourceDirArg.add_argument(parser)
    NewsStartFromIndexArg.add_argument(parser)
    ParseFramesInSentencesArgs.add_argument(parser)
    RuSentiFramesCacheArgs.add_argument(parser)
    NerTypeArg.add_argument(parser)
    NerCacheFilepathArg.add_argument(parser)
    FramesCacheDirArg.add_argument(parser)
    SourceNewsReaderArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    task = args.task[0]
    ner_cache_filepath = NerCacheFilepathArg.read_argument(args)
    frames_cache_dir = FramesCacheDirArg.read_argument(args)
    ner_type = NerTypeArg.read_argument(args)
    src_dir = NewsSourceDirArg.read_argument(args)
    out_dir = OutputDirArg.read_argument(args)
    use_ner_cache_only = args.use_ner_cache
    restore_missed_objects = args.restore_missed_objects
    parse_frames_in_sents = ParseFramesInSentencesArgs.read_argument(args)
    rusentiframes_filepath = RuSentiFramesCacheArgs.read_argument(args)
    start_from_index = NewsStartFromIndexArg.read_argument(args)
    synonyms_filepath = SynonymsCollectionFilepathArg.read_argument(args)
    reader = SourceNewsReaderArg.read_argument(args)

    # Setup text processing settings.
    settings = Settings(use_auth_list=args.use_auth_list,
                        ner_name=ner_type,
                        use_ner_cache_only=use_ner_cache_only,
                        frames_collection_filepath=rusentiframes_filepath,
                        restore_missed_objects=restore_missed_objects,
                        synonyms_collection_filepath=synonyms_filepath)

    # Setup ner cache
    ner_cache = SQLiteNERCacheData.init_as_read_only(ner_cache_filepath)
    settings.set_ner_cache(ner_cache)

    # Setup frame cache
    frames_cache = SQLiteFramesCacheData.init_as_read_only(
        folder=src_dir if frames_cache_dir is None else frames_cache_dir,
        rusentiframes_version=basename(rusentiframes_filepath),
        parse_sentences=parse_frames_in_sents)
    settings.set_frames_cache(frames_cache)

    task_name = get_task_name(task_index=task_to_index[task],
                              prefix=basename(src_dir),
                              ner_name=ner_type)

    # initialize output dir.
    actual_out_dir = join(out_dir, task_name) \
        if start_from_index == 0 \
        else get_output_root_task_new_part_folder(out_dir=out_dir,
                                                  task_name=task_name)

    with ner_cache:
        with frames_cache:

            print("Output dir:", actual_out_dir)
            news_it = reader.get_news_iter(src_dir, start_with_index=start_from_index)

            if task == TASK_EXTRACTION_BY_PAIRS:
                run_re_by_pairs(news_iter=news_it,
                                out_dir=actual_out_dir,
                                settings=settings,
                                pairs_list_filepath=args.pairs_list_filepath,
                                start_with_text=start_from_index,
                                parse_frames_in_news_sentences=parse_frames_in_sents)

            if task == TASK_EXTRACTION_BY_FRAMES:
                run_re_by_frames(news_iter=news_it,
                                 out_dir=actual_out_dir,
                                 settings=settings,
                                 start_with_text=start_from_index,
                                 parse_frames_in_news_sentences=parse_frames_in_sents)

            elif task == TASK_DIFF_EXTRACTION:
                run_re_diff(news_iter=news_it,
                            out_dir=actual_out_dir,
                            settings=settings,
                            pairs_list_filepath=args.pairs_list_filepath,
                            start_with_text=start_from_index,
                            parse_frames_in_news_sentences=parse_frames_in_sents)
