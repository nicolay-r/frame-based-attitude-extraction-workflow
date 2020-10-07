import sys
import argparse
from os import mkdir
from os.path import join, exists

sys.path.append('../../')

from scripts.args.src_news_reader import SourceNewsReaderArg
from scripts.args.ner_cache import NerCacheFilepathArg
from scripts.args.ner_type import NerTypeArg
from scripts.args.src_news_dir import NewsSourceDirArg
from scripts.args.out_dir import OutputDirArg
from texts.extraction.frame_based.limits import NerTypesLimitation
from texts.extraction import parsed_news_utils
from texts.extraction.settings import Settings
from texts.objects.helper import TextObjectHelper
from texts.objects.cache.sqlite_ner_cache import SQLiteNERCacheData
from texts.readers.utils import NewsInfo


WORD_FILENAME_PREFIX = 'vocab_'
WORD_TYPE_SEPARATOR = "||"


def extract_object_values(sentence, ner_data):
    assert(isinstance(sentence, str))
    assert(isinstance(ner_data, list))

    if len(ner_data) == 0:
        return
        yield

    terms, parsed_text = parsed_news_utils.to_input_terms(text=sentence, ner=None, stemmer=None)

    for obj_desc in ner_data:

        fixed_obj_desc = TextObjectHelper.try_fix_object_value(
            obj_desc=obj_desc,
            input_terms=terms,
            is_term_func=lambda t_ind: parsed_text.is_term(t_ind))

        if fixed_obj_desc is None:
            continue

        l, r = fixed_obj_desc.get_range()
        yield terms[l:r], obj_desc.ObjectType


def iter_for_sentence(filename, s_ind, sentence, is_valid_by_type):
    assert(callable(is_valid_by_type))

    ner_data = ner_cache.try_get(filename=filename, s_ind=s_ind)

    if ner_data is None:
        return
        yield

    for value, obj_type in extract_object_values(sentence=sentence, ner_data=ner_data):

        if not is_valid_by_type(obj_type):
            continue

        yield value, obj_type


def iter_for_news(news_info, is_valid_by_type):
    assert(isinstance(news_info, NewsInfo))

    t_it = iter_for_sentence(filename=news_info.FileName,
                             s_ind=ner_cache.TITLE_SENT_IND,
                             sentence=news_info.Title,
                             is_valid_by_type=is_valid_by_type)
    for value, obj_type in t_it:
        yield value, obj_type

    for s_ind, sentence in enumerate(news_info.iter_sentences()):
        s_it = iter_for_sentence(filename=news_info.FileName,
                                 s_ind=s_ind,
                                 sentence=sentence,
                                 is_valid_by_type=is_valid_by_type)
        for value, obj_type in s_it:
            yield value, obj_type


def get_obj_values_subfolder(output_dir):
    return join(output_dir, ".vocab")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Object values extraction from NER.")

    # Providing arguments.
    NewsSourceDirArg.add_argument(parser)
    NerTypeArg.add_argument(parser)
    OutputDirArg.add_argument(parser)
    NerCacheFilepathArg.add_argument(parser)
    SourceNewsReaderArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    ner_type = NerTypeArg.read_argument(args)
    ner_cache_filepath = NerCacheFilepathArg.read_argument(args)
    output_dir = OutputDirArg.read_argument(args)
    source_dir = NewsSourceDirArg.read_argument(args)
    reader = SourceNewsReaderArg.read_argument(args)

    # Also copy-pasted
    ner_class_type = Settings.get_class_by_ner_name(ner_type)

    limitation = NerTypesLimitation(ner_class_type)

    # Composing output dir.
    obj_values_dir = get_obj_values_subfolder(output_dir)

    # Create a subdirectory for an output results.
    if not exists(obj_values_dir):
        mkdir(obj_values_dir)

    # Initializing ner cache.
    ner_cache = SQLiteNERCacheData.init_as_read_only(ner_cache_filepath)

    # Exporting results.
    news_processed = 0
    added_words = set()
    f_name = "{}.txt".format(ner_type)

    with ner_cache:
        with open(join(obj_values_dir, f_name), "w") as f:
            for text_index, news_info in reader.get_news_iter(source_dir):
                assert(isinstance(news_info, NewsInfo))

                if not ner_cache.is_news_registered(news_id=news_info.FileName):
                    continue

                news_processed += 1

                values_it = iter_for_news(
                    news_info=news_info,
                    is_valid_by_type=lambda _: True)

                for obj_terms, obj_type in values_it:
                    target_value = " ".join(obj_terms).lower().strip()

                    # if target_value in added_words:
                    #     continue

                    f.write("{word}{sep}{type}\n".format(word=target_value,
                                                         sep=WORD_TYPE_SEPARATOR,
                                                         type=obj_type))

    # Saving log
    with open(join(obj_values_dir, 'log_{f_name}.txt'.format(f_name=f_name)), "w") as f:
        f.write("News processed: {}".format(news_processed))
