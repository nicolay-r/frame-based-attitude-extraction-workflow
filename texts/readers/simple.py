from os.path import join

from texts.readers.base import BaseNewsReader
from texts.readers.utils import NewsInfo


class SimpleNewsReader(BaseNewsReader):

    def __init__(self, filename):
        self.__filename = filename

    # BaseNewsReader

    def _iter_news_info(self, src_folder):

        def __create_news_info():
            return NewsInfo(filename=self.__filename + str(text_index),
                            title=title,
                            sentences=sentences)

        with open(self.__create_filepath(src_folder), 'r') as f:

            title = None
            is_title = True
            sentences = []

            text_index = 0
            for line in f.readlines():
                if line == '\n':
                    yield __create_news_info()

                    sentences = []
                    is_title = True
                    title = None
                    text_index += 1

                else:
                    processed_line = line.strip()
                    if is_title:
                        title = processed_line
                        is_title = False
                    else:
                        sentences.append(processed_line)

            if title is not None:
                yield __create_news_info()

    def _calc_total_approx_news_count(self, src_folder):
        count = 0
        with open(self.__create_filepath(src_folder), 'r') as f:
            for line in f.readlines():
                if self.__is_new_sentence(line):
                    count += 1

        return count

    # endregion

    # region private methods

    @staticmethod
    def __is_new_sentence(line):
        return line == '\n'

    def __create_filepath(self, src_folder):
        return join(src_folder, self.__filename)

    # endregion


