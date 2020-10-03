from core.runtime.parser import TextParser
from texts.extraction.default import Default


if __name__ == "__main__":

    stemmer = Default.create_default_stemmer()
    s = TextParser.parse(text="В ,;Кон-грессе, где были м-ы;!.ХA{", stemmer=stemmer)
    print(' '.join(['[{}]'.format(s) for s in s.iter_original_terms()]))
