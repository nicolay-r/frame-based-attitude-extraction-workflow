from itertools import chain
from os.path import join

from core.helpers.frames import FramesHelper
from core.processing.lemmatization.base import Stemmer
from core.source.frames.variants import FrameVariantInText, FrameVariant
from texts.extraction.text_parser import terms_utils
from texts.frames import TextFrameVariantsCollection
from texts.objects.cache.sqlite_base import BaseSQLiteObjectCache
from texts.readers.utils import NewsInfo


class SQLiteFramesCacheData(BaseSQLiteObjectCache):

    # region static fields

    CREATE_TABLE_IF_NOT_EXISTS_SQLITE_CMD = """
        CREATE TABLE IF NOT EXISTS {table} (
            filename TEXT, 
            sentence_ind INTEGER, 
            frames_data TEXT,
            PRIMARY KEY (filename, sentence_ind))
        """
    INSERT_RECORD_SQLITE_CMD = "INSERT INTO {table} VALUES ('{filename}', {s_ind}, '{frames_data}')"

    # endregion

    def __init__(self, stemmer, frames_helper, db_filepath):
        assert(isinstance(stemmer, Stemmer) or stemmer is None)
        assert(isinstance(frames_helper, FramesHelper) or frames_helper is None)
        assert(isinstance(db_filepath, str) or db_filepath is None)
        super(SQLiteFramesCacheData, self).__init__(db_filepath=db_filepath)
        self.__stemmer = stemmer
        self.__frames_helper = frames_helper

    @classmethod
    def init_for_rw(cls, stemmer, frames_helper, rusentiframes_version, parse_sentences, folder):
        db_filepath = SQLiteFramesCacheData.__create_db_name(
            rusentiframes_version=rusentiframes_version,
            parse_sentences=parse_sentences,
            folder=folder)

        return cls(stemmer=stemmer,
                   frames_helper=frames_helper,
                   db_filepath=db_filepath)

    @classmethod
    def init_as_read_only(cls, folder, rusentiframes_version, parse_sentences):
        assert(isinstance(folder, str))

        db_filepath = SQLiteFramesCacheData.__create_db_name(
            rusentiframes_version=rusentiframes_version,
            parse_sentences=parse_sentences,
            folder=folder)

        print("Using the following Frames cache: {}".format(db_filepath))

        return cls(stemmer=None,
                   frames_helper=None,
                   db_filepath=db_filepath)

    # region public methods

    @staticmethod
    def get_table_name():
        return "frames"

    def register_news(self, news_info,
                      process_inner_sentences,
                      is_valid_frames_collection_in_title=lambda _: True):
        assert(isinstance(news_info, NewsInfo))
        assert(isinstance(process_inner_sentences, bool))
        assert(callable(is_valid_frames_collection_in_title))

        filename = news_info.FileName

        # Skipping existed news.
        if self._is_news_exists_in_cache(filename):
            return

        s_it = self.__iter_sentences(news_info=news_info,
                                     process_inner_sentences=process_inner_sentences)

        for s_ind, lemma_terms in s_it:

            accepted = self.__register_sentence(filename=filename,
                                                lemmas=lemma_terms,
                                                s_ind=s_ind,
                                                check_title_func=is_valid_frames_collection_in_title)

            if not accepted:
                break

        # Commiting results into database.
        self._conn.commit()

    @staticmethod
    def __create_db_name(rusentiframes_version, parse_sentences, folder):
        assert(isinstance(parse_sentences, bool))
        return join(folder, "frames_cache_{rusentiframes_version}_{parse_mode}.db".format(
            rusentiframes_version=rusentiframes_version,
            parse_mode="full" if parse_sentences else "titles"))

    def __register_sentence(self, filename, lemmas, s_ind, check_title_func):
        assert(isinstance(filename, str))
        assert(isinstance(s_ind, int))
        assert(isinstance(lemmas, list))
        assert(callable(check_title_func))

        frame_variants_collection = TextFrameVariantsCollection.from_parsed_text(
            lemmas=lemmas,
            frames_helper=self.__frames_helper)

        if s_ind == self.TITLE_SENT_IND:
            if not check_title_func(frame_variants_collection):
                # Whole text asuumes to be skipped
                return False

        if len(frame_variants_collection) > 0:
            # Register only if we have a non-empty result.

            request = self.INSERT_RECORD_SQLITE_CMD.format(
                table=self.get_table_name(),
                filename=filename,
                s_ind=s_ind,
                frames_data=self.__serialize_frames_data(frame_variants_collection))

            self._cursor.execute(request)

        return True

    def __iter_sentences(self, news_info, process_inner_sentences):
        assert(isinstance(news_info, NewsInfo))
        assert(isinstance(process_inner_sentences, bool))

        s_it = chain([news_info.Title],
                     news_info.iter_sentences() if process_inner_sentences else [])

        for s_ind, sentence in enumerate(s_it):
            assert(isinstance(sentence, str))

            lemma_terms = terms_utils.to_input_terms(text=sentence,
                                                     stemmer=self.__stemmer,
                                                     ner=None,
                                                     lemmatized_terms=True,
                                                     return_parsed_text=False)

            yield s_ind - 1, lemma_terms

    # endregion

    # region private methods

    @staticmethod
    def __serialize_frames_data(frame_variants_collection):
        assert(isinstance(frame_variants_collection, TextFrameVariantsCollection))

        s_variants = []

        for fv in frame_variants_collection:
            assert(isinstance(fv, FrameVariantInText))

            data = [str(fv.Position),
                    '1' if fv.IsInverted else '0',
                    SQLiteFramesCacheData.__serialize_variant(fv.Variant)]

            s_fv = BaseSQLiteObjectCache.PARAMS_SEP.join(data)

            s_variants.append(s_fv)

        return BaseSQLiteObjectCache.ENTRY_SEP.join(s_variants)

    @staticmethod
    def __serialize_variant(frame_variant):
        assert(isinstance(frame_variant, FrameVariant))
        data = [frame_variant.get_value(), frame_variant.FrameID]
        return BaseSQLiteObjectCache.PARAMS_SEP.join(data)

    # endregion

    def __enter__(self):
        super(SQLiteFramesCacheData, self).__enter__()
        self._cursor.execute(self.CREATE_TABLE_IF_NOT_EXISTS_SQLITE_CMD.format(table=self.get_table_name()))

    # region protected methods

    def _deserialize_item(self, data_item):
        assert (isinstance(data_item, str))
        pos, is_inverted, var_text, var_frame_id = data_item.split(self.PARAMS_SEP)
        variant = FrameVariant(text=var_text, frame_id=var_frame_id)
        return FrameVariantInText(variant=variant,
                                  start_index=int(pos),
                                  is_inverted=True if int(is_inverted) == 1 else False)

    # endregion
