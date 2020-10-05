from core.evaluation.labels import NeutralLabel
from core.runtime.parser import ParsedText
from core.runtime.ref_opinon import RefOpinion
from texts.extraction.frame_based.process import FrameDependentTextProcessor
from texts.printing.quiz import QuizPrinter
from texts.printing.utils import ContextDescriptor


class QuizTextProcessor(FrameDependentTextProcessor):

    def __init__(self,
                 settings,
                 contexts_printer,
                 opinion_statistic_printer,
                 parse_frames_in_news_sentences,
                 quiz_printer):
        assert(isinstance(quiz_printer, QuizPrinter))

        super(QuizTextProcessor, self).__init__(
            settings=settings,
            contexts_printer=contexts_printer,
            parse_frames_in_news_sentences=parse_frames_in_news_sentences,
            opinion_statistic_printer=opinion_statistic_printer)

        self.__quiz_printer = quiz_printer
        self.__printed_texts = set()

    def process_news(self, text_index, news_info):
        pass

    @staticmethod
    def __sentence_to_key(parsed_sentence):
        assert(isinstance(parsed_sentence, ParsedText))
        lemmas = []
        for lemma in parsed_sentence.iter_lemmas(return_raw=True):
            if isinstance(lemma, str):
                lemmas.append(lemma)
        return ' '.join(lemmas)

    def process_news_and_print(self, text_index, news_info, terms_in_sentence_limit=20):

        processed_result = self.process_news_core(text_index=text_index,
                                                  news_info=news_info)

        if processed_result is None:
            return

        print_title = True
        td, cds, text_opinions = processed_result
        for cd_i, cd in enumerate(cds):
            assert(isinstance(cd, ContextDescriptor))

            if len(cd.parsed_text) > terms_in_sentence_limit:
                continue

            if cd_i == 0:
                continue

            for i, opinion_ref in enumerate(cd.opinion_refs):
                assert(isinstance(opinion_ref, RefOpinion))

                cd.opinion_refs[i] = RefOpinion(left_index=opinion_ref.LeftIndex,
                                                right_index=opinion_ref.RightIndex,
                                                sentiment=NeutralLabel())

            s_key = self.__sentence_to_key(cd.parsed_text)

            if s_key not in self.__printed_texts:
                self.__quiz_printer.print_extracted_opinion(title_descriptor=td,
                                                            context_descriptor=cd,
                                                            print_title=print_title)
                self.__printed_texts.add(s_key)
                print_title = False
