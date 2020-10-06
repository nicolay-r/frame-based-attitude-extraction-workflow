# -*- coding: utf-8 -*-
from os.path import join

from texts.printing.utils import TitleDescriptor, \
    print_objects, \
    print_opinions, \
    print_frame_variants, \
    ContextDescriptor


class ContextsPrinter:

    FILE_KEY = 'File'
    NEWS_SEP_KEY = '----------\n'

    def __init__(self, dir, prefix, opins_per_file=10000):
        assert(isinstance(dir, str))
        assert(isinstance(prefix, str))
        self.__file_index = 0
        self.__opinions_written = 0
        self.__dir = dir
        self.__prefix = prefix
        self.__out = None
        self.__opins_per_file = opins_per_file
        self.__last_text_index_written = -1

    def print_news_title(self, title_descriptor):
        assert(isinstance(title_descriptor, TitleDescriptor))

        if title_descriptor.text_index == self.__last_text_index_written:
            return

        if self.__out is None:
            self.__out = self.__open_file()

        if self.__opinions_written > self.__opins_per_file:
            self.__opinions_written = 0
            self.__reopen_new_file()
        else:
            self.__opinions_written += 1

        self.__print_extracted_title(title_descriptor)
        self.__last_text_index_written = title_descriptor.text_index

    def __open_file(self):
        return open(join(self.__dir, "{}_{}.txt".format(self.__prefix,
                                                         "{0:04d}".format(self.__file_index))),
                    "w")

    def __reopen_new_file(self):
        self.__out.close()
        self.__file_index += 1
        self.__out = self.__open_file()

    def __print_extracted_title(self, title_descriptor):
        assert(isinstance(title_descriptor, TitleDescriptor))
        td = title_descriptor

        self.__out.writelines(self.NEWS_SEP_KEY)

        s = "{template}: {name}\n".format(template=self.FILE_KEY,
                                          name=td.news_info.FileName)
        self.__out.writelines(s)

        s = "SentencesCount: {}\n".format(len(td.news_info))
        self.__out.writelines(s)

        print_objects(self.__out, td.objects_collection)

        print_opinions(f=self.__out,
                       opinion_refs=td.opinion_refs,
                       objects_collection=td.objects_collection)

        print_frame_variants(f=self.__out,
                             text_frames=td.title_frames,
                             frames=td.frames)

        s = "TermsInTitle: {}\n".format(len(td.parsed_title))
        self.__out.writelines(s)

        s = "Title: {}\n".format(td.parsed_title.to_string())
        self.__out.writelines(s)

    def print_extracted_opinion(self, context_descriptor):
        assert(isinstance(context_descriptor, ContextDescriptor))
        cd = context_descriptor

        s = "Sentence: {}\n".format(cd.sentence_index)
        self.__out.writelines(s)

        print_objects(f=self.__out,
                      objects_collection=cd.objects_collection)

        print_opinions(f=self.__out,
                       opinion_refs=cd.opinion_refs,
                       objects_collection=cd.objects_collection)

        print_frame_variants(f=self.__out,
                             text_frames=cd.text_frames,
                             frames=cd.frames)

        s = "TermsInText: {}\n".format(len(cd.parsed_text))
        self.__out.writelines(s)

        s = "Text: {}\n".format(cd.parsed_text.to_string())
        self.__out.writelines(s)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__out.close()