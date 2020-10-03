
class SentenceDescriptor:

    def __init__(self,
                 text_index,
                 sentence_index):
        self.__text_index = text_index
        self.__sentence_index = sentence_index

    @property
    def TextIndex(self):
        return self.__text_index

    @property
    def SentenceIndex(self):
        return self.__sentence_index

    def to_str(self):
        return "text: {}, sentence: {}".format(self.__text_index, self.__sentence_index)
