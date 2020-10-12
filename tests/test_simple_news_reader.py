from texts.readers.simple import SimpleNewsReader
from texts.readers.utils import NewsInfo


if __name__ == "__main__":

    sr = SimpleNewsReader('sample.txt')
    for text_index, news_info in sr.get_news_iter('../data'):
        assert(isinstance(news_info, NewsInfo))
        print(text_index)
        print(news_info.Title)
        print(news_info.sentences_count())