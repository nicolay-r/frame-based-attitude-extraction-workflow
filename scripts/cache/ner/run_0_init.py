import sys

sys.path.append('../../../')

import argparse
from core.processing.lemmatization.base import Stemmer
from core.processing.ner.base import NamedEntityRecognition
from texts.readers.base import BaseNewsReader
from scripts.args.ner_type import NerTypeArg
from scripts.args.news import NewsStartFromIndexArg
from scripts.args.src_news_dir import NewsSourceDirArg
from scripts.args.src_news_reader import SourceNewsReaderArg
from texts.extraction.default import Default
from texts.extraction.settings import Settings
from texts.extraction.frame_based.limits import NerTypesLimitation
from texts.objects.cache.sqlite_ner_cache import SQLiteNERCacheData


def filter_title_by_ner_types(ner, types, predefined_set):
    """
    Opinion could not be organized it there there are no at least two objects of the following types:
        [ORG, PERSON, GPE]
    """
    assert(isinstance(ner, NamedEntityRecognition))
    assert(isinstance(types, list))
    assert(isinstance(predefined_set, set))

    relevant_types_found = 0

    for t in types:
        if t in predefined_set:
            relevant_types_found += 1

    return relevant_types_found >= 2


def run_ner_cache(reader, src_dir, ner, stemmer, start_from_index):
    assert(isinstance(reader, BaseNewsReader))
    assert(isinstance(src_dir, str))
    assert(isinstance(ner, NamedEntityRecognition))
    assert(isinstance(stemmer, Stemmer))
    assert(isinstance(start_from_index, int))

    # Populating cache.
    cache = SQLiteNERCacheData.init_for_rw(stemmer=stemmer,
                                           folder=src_dir,
                                           ner=ner)

    limitation = NerTypesLimitation(type(ner))

    with cache:
        for news_index, news_info in reader.get_news_iter(src_dir):

            if news_index < start_from_index:
                continue

            cache.register_news(news_info=news_info,
                                is_valid_title_by_ner_types=lambda types: filter_title_by_ner_types(
                                    ner=ner,
                                    types=types,
                                    predefined_set=limitation.SupportedNerTypesSet))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="NER (Named Entity Recognition) results caching for a particular Source.")

    # Providing arguments.
    NewsSourceDirArg.add_argument(parser)
    SourceNewsReaderArg.add_argument(parser)
    NewsStartFromIndexArg.add_argument(parser)
    NerTypeArg.add_argument(parser)

    # Parsing arguments.
    args = parser.parse_args()

    # Reading arguments.
    src_dir = NewsSourceDirArg.read_argument(args)
    reader = SourceNewsReaderArg.read_argument(args)
    ner_type = NerTypeArg.read_argument(args)
    start_from_index = NewsStartFromIndexArg.read_argument(args)

    run_ner_cache(reader=reader,
                  src_dir=src_dir,
                  ner=Settings.get_class_by_ner_name(ner_type)(),
                  stemmer=Default.create_default_stemmer(),
                  start_from_index=start_from_index)
