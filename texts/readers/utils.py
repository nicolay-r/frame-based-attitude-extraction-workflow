# -*- coding: utf-8 -*-

__signs = ['.', '?', '!', '…', ':', ';']
__limited = ['обл.', 'ул.', 'пр.']


class NewsInfo:
    """
    Descriptor of News
    Returns as a result of iteration through collection.
    """

    def __init__(self, filename, title, sentences):
        assert(isinstance(filename, str))
        assert(isinstance(title, str))
        assert(isinstance(sentences, list))
        self.__filename = filename
        self.__sentences = sentences
        self.__title = title

    @property
    def Title(self):
        return self.__title

    @property
    def FileName(self):
        return self.__filename

    def iter_sentences(self):
        for p in self.__sentences:
            yield p

    def __len__(self):
        return len(self.__sentences)


def iter_text_by_nonempty_sentences(original_text):
    assert(isinstance(original_text, str))
    for sentence in __iter_text_by_sentences(original_text):
        sentence = sentence.strip()
        if len(sentence) == 0:
            continue
        yield sentence


def __iter_text_by_sentences(original_text):
    assert(isinstance(original_text, str))
    last = 0
    has_output = False
    chars_to_skip = 0
    for i, char in enumerate(original_text):

        if chars_to_skip > 0:
            chars_to_skip -= 1
            continue

        if i + 2 >= len(original_text):
            break

        is_end = False

        if char == '\n' and original_text[i + 1].isupper():
            is_end = True

        if char in __signs:

            w_prior = __get_prior_word(original_text, i)
            w_next = __get_next_word(original_text, i + 1)

            if char == ':' and w_prior.isdigit() and w_next.isdigit():
                chars_to_skip = len(w_next)
                is_end = True

            elif not (len(w_prior) == 1 or w_prior in __limited):

                if original_text[i + 1] == '\n':
                    is_end = True

                if (w_next[0].isupper() or w_next[0].isdigit() or w_next[0] in ['\"', '«', '–']):
                    is_end = True

                if (i > 0 and original_text[i - 1].islower() and w_next[0].isupper()):
                    is_end = True

        if is_end:
            to = i + 1 + chars_to_skip
            yield original_text[last:to]
            last = to
            has_output = True

    if not has_output:
        yield original_text


def __get_prior_word(original_text, position):
    i = position
    while i >= 0 and original_text[i] != ' ':
        i -= 1
    return original_text[i+1:position]


def __get_next_word(original_text, position):
    i = position
    while i < len(original_text) and original_text[i].isspace():
        i += 1
    j = i
    while j < len(original_text) and not original_text[j].isspace():
        j += 1
    return original_text[i:j]


