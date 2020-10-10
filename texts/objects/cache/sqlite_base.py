import sqlite3
from texts.objects.cache.base import BaseObjectCache


class BaseSQLiteObjectCache(BaseObjectCache):

    CHECK_NEWS_EXISTS = "SELECT EXISTS (SELECT 1 FROM {table} WHERE filename=? LIMIT 1)"
    SELECT_NEWS_SQLITE_CMD = "SELECT * from {table} where filename=?"

    PARAMS_SEP = ','
    ENTRY_SEP = ';'

    def __init__(self, db_filepath):
        assert(isinstance(db_filepath, str) or db_filepath is None)
        super(BaseSQLiteObjectCache, self).__init__()

        self.__db_filepath = db_filepath
        self._cursor = None

        self.__fetched_filename = None
        self.__fetched_data = {}

    # region public methods

    def try_get(self, filename, s_ind):
        if self.__fetched_filename != filename:

            # Loading from sqlite.
            select = self.SELECT_NEWS_SQLITE_CMD.format(table=self.get_table_name())
            self._cursor.execute(select, (filename,))

            # Composing data.
            records = self._cursor.fetchall()

            if len(records) == 0:
                # not existed in cache
                return None

            self.__fetched_data.clear()
            for record in records:
                _, rec_s_ind, data = record
                self.__fetched_data[rec_s_ind] = self.__deserialize_data(data)

            # update filename key of a cached results.
            self.__fetched_filename = filename

        # Some sentence might be ommited.
        if s_ind not in self.__fetched_data:
            return None

        # Getting related data.
        return self.__fetched_data[s_ind]

    @staticmethod
    def get_table_name():
        raise NotImplementedError()

    def is_news_registered(self, news_id):
        return self._is_news_exists_in_cache(news_id)

    # endregion

    # region private methods

    def __deserialize_data(self, data):
        assert(isinstance(data, str))
        objects = data.split(self.ENTRY_SEP)
        return [self._deserialize_item(obj) for obj in objects if obj != ""]

    # endregion

    # region protected methods

    def _is_news_exists_in_cache(self, filename):
        check_request = self.CHECK_NEWS_EXISTS.format(table=self.get_table_name())
        result = self._cursor.execute(check_request, (filename,))
        return result.fetchone()[0]

    @staticmethod
    def _deserialize_item(obj):
        pass

    # endregion

    # region base overriden methods

    def __enter__(self):
        self._conn = sqlite3.connect(self.__db_filepath)
        self._cursor = self._conn.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.close()
        self._conn.close()

    # endregion
