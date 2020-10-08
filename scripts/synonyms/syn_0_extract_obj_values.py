import sys
import argparse
from os.path import join

sys.path.append('../../')

from io_utils import create_dir
from scripts.args.src_news_reader import SourceNewsReaderArg
from scripts.args.ner_cache import NerCacheFilepathArg
from scripts.args.ner_type import NerTypeArg
from scripts.args.src_news_dir import NewsSourceDirArg
from scripts.args.out_dir import OutputDirArg
from scripts.synonyms.values_extractor import TextObjectValuesExtractor
from texts.objects.authorized.object import AuthTextObject
from texts.extraction.default import Default
from texts.extraction.frame_based.obj_auth import TextObjectAuthorizer
from texts.objects.cache.sqlite_ner_cache import SQLiteNERCacheData
from texts.readers.utils import NewsInfo


WORD_TYPE_SEPARATOR = "||"


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

    # Initializing ner cache.
    ner_cache = SQLiteNERCacheData.init_as_read_only(ner_cache_filepath)

    # Exporting results.
    news_processed = 0
    added_words = set()
    f_name = "{}.txt".format(ner_type)

    # Init obj values extractor.
    ner_class_type = Default.get_class_by_ner_name(ner_type)
    text_object_authorizer = TextObjectAuthorizer(ner_type=ner_class_type)
    obj_values_extractor = TextObjectValuesExtractor(
        ner_cache=ner_cache,
        stemmer=Default.create_default_stemmer(),
        default_auth_check=lambda text_obj: text_object_authorizer.is_auth(text_obj))

    create_dir(output_dir)
    print("Output dir: {}".format(output_dir))

    with ner_cache:
        with open(join(output_dir, f_name), "w") as f:
            for _, news_info in reader.get_news_iter(source_dir):
                assert(isinstance(news_info, NewsInfo))

                if not ner_cache.is_news_registered(news_id=news_info.FileName):
                    continue

                news_processed += 1

                for obj in obj_values_extractor.iter_for_news(news_info=news_info):
                    assert(isinstance(obj, AuthTextObject))

                    if not obj.IsAuthorized:
                        continue

                    value = obj.get_value()

                    if value in added_words:
                        continue

                    f.write("{word}{sep}{type}\n".format(word=value,
                                                         sep=WORD_TYPE_SEPARATOR,
                                                         type=obj.Type))

                    added_words.add(value)

    # Saving log
    with open(join(output_dir, 'log_{f_name}.txt'.format(f_name=f_name)), "w") as f:
        f.write("News processed: {}".format(news_processed))
