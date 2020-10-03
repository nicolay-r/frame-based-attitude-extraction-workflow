class RussianThesaurusSenses:

    NAME_XML_ARG_TEMPLATE = 'name="'
    LEMMA_XML_ARG_TEMPLATE = 'lemma="'
    MWORD_XML_ARG_TEMPLATE = 'main_word="'

    def __init__(self, mw_by_name, mw_by_lemma):
        self.mw_by_name = mw_by_name
        self.mw_by_lemma = mw_by_lemma

    @classmethod
    def from_xml_file(cls, filepath):

        mw_by_name = {}
        mw_by_lemma = {}

        with open(filepath, 'r') as f:
            for line in f.readlines():

                if cls.NAME_XML_ARG_TEMPLATE not in line or \
                   cls.LEMMA_XML_ARG_TEMPLATE not in line or \
                   cls.MWORD_XML_ARG_TEMPLATE not in line:
                    continue

                print(line)

                name = cls.__read_arg(line, cls.NAME_XML_ARG_TEMPLATE).lower()
                lemma = cls.__read_arg(line, cls.LEMMA_XML_ARG_TEMPLATE).lower()
                main_word = cls.__read_arg(line, cls.MWORD_XML_ARG_TEMPLATE).lower()

                if name not in mw_by_name:
                    mw_by_name[name] = main_word
                if lemma not in mw_by_lemma:
                    mw_by_lemma[lemma] = main_word

        return cls(mw_by_name=mw_by_name,
                   mw_by_lemma=mw_by_lemma)

    # region private methods

    @staticmethod
    def __read_arg(line, template):
        if template not in line:
            return None
        begin = line.index(template) + len(template)
        end = line.index('"', begin)

        return line[begin:end]

    # endregion

    # region Public methods

    def get_main_word_by_word(self, word):
        assert(isinstance(word, str))

        if word not in self.mw_by_lemma:
            return None

        return self.mw_by_name[word]

    def get_main_word_by_lemma(self, lemma):
        assert(isinstance(lemma, str))

        if lemma not in self.mw_by_lemma:
            return None

        return self.mw_by_lemma[lemma]

    # endregion