from itertools import chain
from os.path import join

from core.processing.lemmatization.base import Stemmer
from core.processing.ner.base import NamedEntityRecognition
from core.processing.ner.obj_decs import NerObjectDescriptor
from texts.extraction.text_parser import terms_utils
from texts.objects.cache.sqlite_base import BaseSQLiteObjectCache
from texts.readers.utils import NewsInfo


class SQLiteNERCacheData(BaseSQLiteObjectCache):

    """
    NOTE: There is a bug in deep_pavlov == 0.11.0 -- returns an invalid data
    for other elements in batch (>1).
    With deep_ner it is OK, so the size might be increased which is positively
    affects on the processing performance
    """

    # region static fields

    BATCH_SIZE = 1

    CREATE_TABLE_IF_NOT_EXISTS_SQLITE_CMD = """
        CREATE TABLE IF NOT EXISTS {table} (
            filename TEXT, 
            sentence_ind INTEGER, 
            ner_data TEXT,
            PRIMARY KEY (filename, sentence_ind))
        """
    INSERT_RECORD_SQLITE_CMD = "INSERT INTO {table} VALUES ('{filename}', {s_ind}, '{ner_data}')"
    SELECT_BY_SENTENCE_IND = "SELECT ner_data from {table} where sentence_ind=?"

    # endregion

    def __init__(self, stemmer, ner, db_filepath):
        assert(isinstance(stemmer, Stemmer) or stemmer is None)
        assert(isinstance(ner, NamedEntityRecognition) or ner is None)

        super(SQLiteNERCacheData, self).__init__(db_filepath=db_filepath)

        self.__ner = ner

        self.__stemmer = None
        if ner is not None:
            self.__stemmer = stemmer if ner.NeedLemmatization else None

    # region class methods

    @classmethod
    def init_for_rw(cls, stemmer, ner, folder):
        db_filepath = SQLiteNERCacheData.__create_db_name(ner_name=str(ner), folder=folder)
        return cls(stemmer=stemmer, ner=ner, db_filepath=db_filepath)

    @classmethod
    def init_as_read_only(cls, filepath):
        return cls(stemmer=None, ner=None, db_filepath=filepath)

    # endregion

    # region public methods

    @staticmethod
    def get_table_name():
        return "cache"

    def register_news(self, news_info, is_valid_title_by_ner_types=None):
        assert(isinstance(news_info, NewsInfo))
        assert(callable(is_valid_title_by_ner_types) or is_valid_title_by_ner_types is None)

        filename = news_info.FileName

        # Skipping existed news.
        if self._is_news_exists_in_cache(filename):
            return

        batches_it = self.__iter_sentences_grouped_in_batches(
            news_info=news_info,
            reject_by_non_valid_title=True)

        check_title_func = is_valid_title_by_ner_types \
            if is_valid_title_by_ner_types is not None else \
            lambda types: True

        for s_inds, s_input_terms in batches_it:
            accepted = self.__register_sentences(filename=filename,
                                                 input_sequences=s_input_terms,
                                                 s_inds=s_inds,
                                                 is_valid_title_by_ner_types=check_title_func)

            if not accepted:
                break

        # Commiting results into database.
        self._conn.commit()

    # endregion

    # region private methods

    @staticmethod
    def __create_db_name(ner_name, folder):
        return join(folder, "ner_cache_{ner_name}.db".format(ner_name=ner_name))

    def __iter_sentences_grouped_in_batches(self, news_info, reject_by_non_valid_title):
        assert(isinstance(news_info, NewsInfo))
        assert(isinstance(reject_by_non_valid_title, bool))

        b_inds, b_sentences = [], []

        def need_release():
            return len(b_inds) > 0

        it_contents = chain([news_info.Title], news_info.iter_sentences())
        for s_ind, sentence in enumerate(it_contents):
            assert(isinstance(sentence, str))

            actual_ind = s_ind - 1

            if len(b_inds) == self.BATCH_SIZE:
                # release.
                yield b_inds, b_sentences
                b_inds, b_sentences = [], []

            s_input_terms = terms_utils.to_input_terms(
                text=sentence,
                stemmer=self.__stemmer,
                ner=self.__ner,
                return_parsed_text=False)

            if self.__is_valid_input(s_input_terms):
                # add in list.
                b_inds.append(actual_ind)
                b_sentences.append(s_input_terms)
            elif self.__is_title(actual_ind) and reject_by_non_valid_title:
                break

        # release residual part if exists.
        if need_release():
            yield b_inds, b_sentences

    def __is_title(self, s_ind):
        return s_ind == self.TITLE_SENT_IND

    def __serialize_ner_data(self, ner_objs_data):
        assert(isinstance(ner_objs_data, list))
        
        objects = []
        for obj_desc in ner_objs_data:
            assert(isinstance(obj_desc, NerObjectDescriptor))
            s_obj = self.PARAMS_SEP.join([str(obj_desc.Position),
                                          str(obj_desc.Length),
                                          obj_desc.ObjectType])
            objects.append(s_obj)

        return self.ENTRY_SEP.join(objects)

    def __register_sentences(self, filename, input_sequences, s_inds, is_valid_title_by_ner_types):
        assert(len(input_sequences) > 0)
        assert(callable(is_valid_title_by_ner_types))

        ner_data = self.__ner.extract(input_sequences, return_single=False)

        first_obj_desc = ner_data[0]
        assert(isinstance(first_obj_desc, NerObjectDescriptor))

        # checking title by ner types appeared in it
        if s_inds[0] == self.TITLE_SENT_IND and not is_valid_title_by_ner_types(first_obj_desc.ObjectType):
            return False

        # composing requests.
        for seq_ind in range(len(input_sequences)):
            request = self.INSERT_RECORD_SQLITE_CMD.format(
                table=self.get_table_name(),
                filename=filename,
                s_ind=s_inds[seq_ind],
                ner_data=self.__serialize_ner_data(ner_data))

            self._cursor.execute(request)

        return True

    def __is_valid_input(self, input_sequence):
        return self.__ner.InputLimitation > len(input_sequence) > 0

    # endregion

    # region protected methods

    def _deserialize_item(self, data_item):
        assert (isinstance(data_item, str))
        pos, length, obj_type = data_item.split(BaseSQLiteObjectCache.PARAMS_SEP)
        return NerObjectDescriptor(pos=int(pos),
                                   length=int(length),
                                   obj_type=obj_type)

    # endregion

    def __enter__(self):
        super(SQLiteNERCacheData, self).__enter__()
        self._cursor.execute(self.CREATE_TABLE_IF_NOT_EXISTS_SQLITE_CMD.format(table=self.get_table_name()))

